#! /usr/bin/env python

import random
import torch
import torch.optim as optim

from collections import defaultdict
from itertools import chain
from pathlib import Path
from pymimir import DomainParser, ProblemParser, Domain, Problem, GroundedSuccessorGenerator, StateSpace, State
from torch_geometric.data import Data
from torch_geometric.nn import GraphConv, aggr, global_add_pool
from torch.nn import Linear, Mish, Sequential, Module, Embedding
from tqdm import tqdm
from typing import List, Tuple, Union

from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph


# Seems to work:
# GraphConv, SAGEConv, GIN

# Can maybe work:
# TransformerConv

class GNN(Module):
    def __init__(self, num_embeddings, embedding_size, num_layers):
        super(GNN, self).__init__()
        # self._layer_conv = GraphConv(embedding_size, embedding_size, aggr=aggr.SoftmaxAggregation())
        self._layer_conv = GraphConv(embedding_size, embedding_size, aggr=aggr.MaxAggregation())
        # self._layer_conv = GraphConv(embedding_size, embedding_size, aggr=aggr.SumAggregation())
        self._update_mlp = Sequential(Linear(embedding_size, embedding_size), Mish(), Linear(embedding_size, embedding_size))
        self._readout_mlp = Sequential(Linear(embedding_size, embedding_size), Mish(), Linear(embedding_size, 1))
        self._embedding = Embedding(num_embeddings, embedding_size)
        self._num_layers = num_layers

    def forward(self, x, edge_index, batch):
        for _ in range(self._num_layers):
            x = x + self._update_mlp(self._layer_conv(x, edge_index))
        x = global_add_pool(x, batch)
        x = self._readout_mlp(x)
        return x

    def get_embedding(self, indices: torch.tensor):
        return self._embedding(indices)


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._logger = initialize_logger("gnn")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        add_console_handler(self._logger)


    def _parse_instance(self) -> Tuple[Domain, Problem]:
        domain_parser = DomainParser(str(self._domain_file_path))
        problem_parser = ProblemParser(str(self._problem_file_path))
        domain = domain_parser.parse()
        problem = problem_parser.parse(domain)
        return domain, problem


    def _generate_state_space(self, problem: Problem) -> Union[StateSpace, None]:
        successor_generator = GroundedSuccessorGenerator(problem)
        return StateSpace.new(problem, successor_generator, 1_000_000)


    def _partition_with_nauty(self, state_value_pairs: List[Tuple[State, int]], progress_bar: bool) -> List[List[Tuple[State, StateGraph]]]:
        partitions = defaultdict(list)
        for state, value in tqdm(state_value_pairs, mininterval=0.5, disable=not progress_bar):
            state_graph = StateGraph(state, skip_nauty=False)
            exact_key = state_graph.nauty_certificate, state_graph.uvc_graph.get_color_histogram()
            partitions[exact_key].append((state, value, state_graph))
        return list(partitions.values())


    def _to_input(self, state_graph_list: List[StateGraph], model: GNN, device) -> Data:
        nodes = []
        sources = []
        targets = []
        batch = []
        offset = 0

        for index, state_graph in enumerate(state_graph_list):
            uvc_vertices = list(state_graph.uvc_graph.vertices.items())
            uvc_edges = list(state_graph.uvc_graph.adj_list.items())
            to_vertex = dict([(id, index + offset) for index, (id, _) in enumerate(uvc_vertices)])
            nodes.extend([data.color.value for _, data in uvc_vertices])
            sources.extend(chain.from_iterable([[to_vertex[id]] * len(neighbors) for id, neighbors in uvc_edges]))
            targets.extend(chain.from_iterable([[to_vertex[id] for id in neighbors] for _, neighbors in uvc_edges]))
            batch.extend([index] * len(uvc_vertices))
            offset += len(uvc_vertices)

        data = Data(model.get_embedding(torch.tensor(nodes, dtype=torch.long, device=device)), torch.tensor([sources, targets], dtype=torch.long, device=device))
        batch = torch.tensor(batch, dtype=torch.long, device=device)
        return data, batch


    def _sample_states(self, state_partitions: List[List[Tuple[State, StateGraph]]], batch_size: int):
        state_values = []
        state_graphs = []
        for _ in range(batch_size):
            _, state_value, state_graph = state_partitions[random.randint(0, len(state_partitions) - 1)][0]
            state_values.append(state_value)
            state_graphs.append(state_graph)
        return state_graphs, state_values


    def run(self):
        """ Main loop for training GNNs for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        _, problem = self._parse_instance()
        progress_bar = self._verbosity == "DEBUG"

        # Generate the state space we will analyze.
        self._logger.info("[Preprocessing] Generating state space...")
        state_space = self._generate_state_space(problem)

        if state_space is None:
            self._logger.info(f"[Preprocessing] State space is too large. Aborting.")
            return

        state_value_pairs = [(state, state_space.get_distance_to_goal_state(state)) for state in state_space.get_states()]
        self._logger.info(f"[Preprocessing] States: {len(state_value_pairs)}")

        # Generate exact equivalence classes.

        self._logger.info("[Nauty] Computing...")
        state_partitions = self._partition_with_nauty(state_value_pairs, progress_bar)
        self._logger.info(f"[Nauty] Partitions: {len(state_partitions)}")

        # Detect which device to use.

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[Training] Device: {device}")

        # Training loop.

        model = GNN(64, 16, 30).to(device)
        optimizer = optim.Adam(model.parameters(), lr=0.0002)

        for i in range(10000):
            optimizer.zero_grad()
            state_graphs, state_values = self._sample_states(state_partitions, 32)
            batch_data, batch_mask = self._to_input(state_graphs, model, device)
            batch_preds = model(batch_data.x, batch_data.edge_index, batch_mask).view(-1)
            batch_labels = torch.tensor(state_values, device=device)
            loss = (batch_preds - batch_labels).square().mean()
            loss.backward()
            optimizer.step()
            if (i % 10) == 0:
                print(f"[Training, {i}] Prediction: {batch_preds.median().item():.3f}, Optimal: {batch_labels.median().item():.3f}, Loss: {loss.item():.3f}")
