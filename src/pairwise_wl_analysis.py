import pykwl as kwl

from collections import defaultdict
from pathlib import Path
from pymimir import Atom, Domain, DomainParser, GroundedSuccessorGenerator, Problem, ProblemParser, State, StateSpace
from typing import List, Tuple, Union, Dict, Any
from itertools import combinations
from dataclasses import dataclass

from .search_node import SearchNode
from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .key_to_int import KeyToInt
from .exact import Driver as ExactDriver


def to_uvc_graph(state: State, coloring_function : KeyToInt, mark_true_goal_atoms: bool) -> kwl.Graph:
    state_graph = StateGraph(state, coloring_function, mark_true_goal_atoms)
    uvc_vertices = state_graph.uvc_graph.vertices
    uvc_edges = state_graph.uvc_graph.adj_list
    to_wl_vertex = {}
    wl_graph = kwl.Graph(False)
    for vertex_id, vertex_data in uvc_vertices.items():
        to_wl_vertex[vertex_id] = wl_graph.add_node(vertex_data.color.value)
    for vertex_id, adjacent_ids in uvc_edges.items():
        for adjacent_id in adjacent_ids:
            wl_graph.add_edge(to_wl_vertex[vertex_id], to_wl_vertex[adjacent_id])
    return wl_graph


@dataclass
class InstanceData:
    id: int
    problem_file_path: str
    goal_distances: Dict[State, int]
    representatives: List[State]
    search_nodes: Dict[State, SearchNode]


class Driver:
    def __init__(self, data_path : Path, verbosity: str, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = (data_path / "domain.pddl").resolve()
        self._problem_file_paths = [file.resolve() for file in data_path.iterdir() if file.is_file() and file.name != "domain.pddl"]
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._ignore_counting = ignore_counting
        self._mark_true_goal_atoms = mark_true_goal_atoms
        add_console_handler(self._logger)


    def _generate_data(self) -> List[InstanceData]:
        instances = []
        for i, problem_file_path in enumerate(self._problem_file_paths):
            try:
                exact_driver = ExactDriver(self._domain_file_path, problem_file_path, "ERROR", False, enable_pruning=True, max_num_states=100_000)
                _, _, goal_distances, representatives, search_nodes = exact_driver.run()
            except MemoryError:
                self._logger.error(f"Out of memory when generating data for problem: {problem_file_path}")
                continue

            if goal_distances is None:
                continue

            self._logger.info(f"[Nauty] Representatives {i}: {len(representatives)}")

            instances.append(InstanceData(i, problem_file_path, goal_distances, representatives, search_nodes))

        return instances


    def _preprocess_data(self, instances: List[InstanceData]) -> Dict[int, Dict[Any, Tuple[State, int]]]:
        partitioning_by_num_vertices = defaultdict(defaultdict)

        for instance in instances:
            for state, goal_distance in instance.goal_distances.items():

                equivalence_key = instance.search_nodes[state].equivalence_class_key

                num_vertices = StateGraph.get_num_vertices(state)

                partitioning_by_num_vertices[num_vertices][equivalence_key] = (state, goal_distance)

        print("[Data processing] Number of partitions by num vertices:", len(partitioning_by_num_vertices))
        print("[Data processing] Initial number of states:", sum(len(instance.goal_distances) for instance in instances))
        print("[Data processing] Final number of states:", sum(len(partition) for partition in partitioning_by_num_vertices.values()))

        return partitioning_by_num_vertices


    def _validate_wl_correctness(self, data: Dict[int, Dict[Any, Tuple[State, int]]], k: int, to_graph, progress_bar: bool) -> Tuple[bool, int]:
        # Check whether the to_graph function can handle states of this sort.
        #for instance in instances:
        #    if to_graph(instance.representatives[0]) is None: return False, -1, -1

        # Test representatives from each partition to see if two are mapped to the same class.
        correct = True
        total_conflicts = 0
        value_conflicts = 0

        count = 0

        for i, key in enumerate(sorted(data.keys())):
            partition = data[key]

            self._logger.info(f"Processing pairs of partition {i} (#vertices in object graph is {key}) with size {len(partition)}")

            for (state_1, v_star_1), (state_2, v_star_2) in combinations(partition.values(), 2):

                if (count > 0 and count % 10_000 == 0):
                    self._logger.info(f"Finished {count} pairs.")

                count += 1

                if (v_star_1 == v_star_2):
                    continue

                wl = kwl.WeisfeilerLeman(k, self._ignore_counting)

                wl_graph_1 = to_graph(state_1)
                num_iterations_1, colors_1, counts_1 = wl.compute_coloring(wl_graph_1)
                coloring_1 = (num_iterations_1, tuple(colors_1), tuple(counts_1))

                wl_graph_2 = to_graph(state_2)
                num_iterations_2, colors_2, counts_2 = wl.compute_coloring(wl_graph_2)
                coloring_2 = (num_iterations_2, tuple(colors_2), tuple(counts_2))

                if (coloring_1 != coloring_2):
                    continue

                correct = False

                total_conflicts += 1
                value_conflicts += 1

                self._logger.info(f"[{k}-FWL] Conflict!")
                self._logger.info(str(coloring_1))
                self._logger.info(str(coloring_2))
                #self._logger.info(f" > instance 1: {instances[i_1].problem_file_path}")
                #self._logger.info(f" > instance 2: {instances[i_2].problem_file_path}")
                self._logger.info(f" > Goal 1: {state_1.get_problem().goal}")
                self._logger.info(f" > Goal 2: {state_2.get_problem().goal}")
                self._logger.info(f" > Cost: {v_star_1}; State 1: {state_1.get_atoms()}")
                self._logger.info(f" > Cost: {v_star_2}; State 2: {state_2.get_atoms()}")

        return correct, total_conflicts, value_conflicts


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        for i, problem_file_path in enumerate(self._problem_file_paths):
            print(f"Problem {i} file:", problem_file_path)
        print()

        progress_bar = self._verbosity == "DEBUG"

        self._logger.info("[Nauty] Generating representatives...")
        instances = self._generate_data()

        self._logger.info("")

        self._logger.info("[Data preprocessing] Preprocessing data...")
        partitioning_by_num_vertices = self._preprocess_data(instances)

        if not instances:
            self._logger.info(f"[Preprocessing] State spaces are too large. Aborting.")
            return

        coloring_function = KeyToInt()

        def run_validation_config(k: int) -> bool:
            correct, total_conflicts, value_conflicts = self._validate_wl_correctness(partitioning_by_num_vertices, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
            tag = f"{k}-FWL, UVC"
            if (not correct) and (total_conflicts < 0): self._logger.info(f"[{tag}] Graph cannot be constructed. Skipping.")
            else: self._logger.info(f"[{tag}] Valid: {correct}; Total Conflicts: {total_conflicts}; Value Conflicts: {value_conflicts}")
            return correct

        # 1-FWL
        self._logger.info("[1-FWL] Computing colorings...")
        valid_1ff = run_validation_config(1)

        # 2-FWL
        #if not valid_1ff:
        #    self._logger.info("[2-FWL] Computing colorings...")
        #    run_validation_config(2)
#
        #self._logger.info("Ran to completion.")
