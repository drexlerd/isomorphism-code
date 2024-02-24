import sys
import time

from pathlib import Path
from collections import defaultdict, deque

from pymimir import DomainParser, ProblemParser, StateSpace, LiftedSuccessorGenerator, GroundedSuccessorGenerator
from tqdm import tqdm

from .state_graph import StateGraph
from .equivalence_graph import EquivalenceGraph
from .logger import initialize_logger, add_console_handler
from .search_node import SearchNode


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, dump_dot: bool, enable_pruning: bool, dump_equivalence_graph: bool, enable_undirected: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._dump_dot = dump_dot
        self._enable_pruning = enable_pruning
        self._dump_equivalence_graph = dump_equivalence_graph
        self._enable_undirected = enable_undirected
        self._logger = initialize_logger("exact")
        self._logger.setLevel(verbosity)
        add_console_handler(self._logger)

    def run(self):
        """ Main loop for computing Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        num_vertices_dec_graph = 0
        num_vertices_dvc_graph = 0
        max_num_edges_dec_graph = 0
        max_num_edges_dvc_graph = 0
        num_generated_states = 0
        equivalence_classes = defaultdict(set)

        domain_parser = DomainParser(str(self._domain_file_path))
        domain = domain_parser.parse()
        problem_parser = ProblemParser(str(self._problem_file_path))
        problem = problem_parser.parse(domain)
        successor_generator = LiftedSuccessorGenerator(problem)

        self._logger.info("Started generating Aut(G)")
        start_time = time.time()
        initial_state = problem.create_state(problem.initial)
        queue = deque()
        queue.append(initial_state)
        closed_list = set()
        closed_list.add(initial_state)
        search_nodes = dict()
        search_nodes[0] = SearchNode(0, None, None)
        num_generated_states += 1

        while queue:
            cur_state = queue.popleft()

            state_graph = StateGraph(cur_state, self._enable_undirected)
            max_num_edges_dec_graph = max(max_num_edges_dec_graph, sum(len(edges) for edges in state_graph.dec_graph.adj_list.values()))
            max_num_edges_dvc_graph = max(max_num_edges_dvc_graph, sum(len(edges) for edges in state_graph.dvc_graph.adj_list.values()))
            num_vertices_dec_graph = len(state_graph.dec_graph.vertices)
            num_vertices_dvc_graph = len(state_graph.dvc_graph.vertices)

            if (num_generated_states % 100 == 1):
                # Overwrite the line in the loop
                print(f"\rAverage time per state: {(time.time() - start_time) / num_generated_states:.2f} seconds", end="")
                sys.stdout.flush()

            # Prune if represenative already exists
            if self._enable_pruning and state_graph.nauty_certificate in equivalence_classes:
                continue
            equivalence_classes[state_graph.nauty_certificate].add(state_graph)

            for applicable_action in successor_generator.get_applicable_actions(cur_state):
                suc_state = applicable_action.apply(cur_state)
                # Prune if state already in closed list
                if suc_state in closed_list:
                    continue
                closed_list.add(suc_state)

                num_generated_states += 1

                queue.append(suc_state)
        print()

        end_time = time.time()
        runtime = end_time - start_time
        self._logger.info("Finished generating Aut(G)")
        print(f"Total time: {runtime:.2f} seconds")
        print("Number of generated states:", num_generated_states)
        print("Number of equivalence classes:", len(equivalence_classes))
        print("Number of vertices in DEC graph:", num_vertices_dec_graph)
        print("Number of vertices in DVC graph:", num_vertices_dvc_graph)
        print("Maximum number of edges in DEC graph:", max_num_edges_dec_graph)
        print("Maximum number of edges in DVC graph:", max_num_edges_dvc_graph)
        print()

        if self._dump_dot:
            print("Dumping dot files to \"outputs/\"")
            Path("outputs/decs").mkdir(parents=True, exist_ok=True)
            Path("outputs/dvcs").mkdir(parents=True, exist_ok=True)
            if self._enable_undirected:
                Path("outputs/uvcs").mkdir(parents=True, exist_ok=True)
            for class_id, state_graphs in enumerate(tqdm(equivalence_classes.values(), file=sys.stdout)):
                Path(f"outputs/dvcs/{class_id}").mkdir(parents=True, exist_ok=True)
                for i, state_graph in enumerate(state_graphs):
                    state_graph.dec_graph.to_dot(f"outputs/decs/{class_id}/{i}.gc")
                    state_graph.dvc_graph.to_dot(f"outputs/dvcs/{class_id}/{i}.gc")
                    if self._enable_undirected:
                        state_graph.uvc_graph.to_dot(f"outputs/uvcs/{class_id}/{i}.gc")
