import sys
import time

from pathlib import Path
from collections import defaultdict

from pymimir import DomainParser, ProblemParser, StateSpace, LiftedSuccessorGenerator
from tqdm import tqdm

from .state_graph import StateGraph
from .logger import initialize_logger, add_console_handler


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, dump_dot: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._dump_dot = dump_dot
        self._logger = initialize_logger("exact")
        self._logger.setLevel(verbosity)
        add_console_handler(self._logger)
        
        if self._dump_dot:
            Path("outputs/decs").mkdir(parents=True, exist_ok=True)
            Path("outputs/dvcs").mkdir(parents=True, exist_ok=True)


    def run(self):
        """ Main loop for computing Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        self._logger.info("Started generating state graph G")
        domain_parser = DomainParser(str(self._domain_file_path))
        domain = domain_parser.parse()
        problem_parser = ProblemParser(str(self._problem_file_path))
        problem = problem_parser.parse(domain)
        state_space = StateSpace.new(problem, LiftedSuccessorGenerator(problem))
        self._logger.info("Finished generating state graph G")
        print("Number of states:", state_space.num_states())
        print("Number of transitions:", state_space.num_transitions())
        print("Number of deadend states:", state_space.num_dead_end_states())
        print("Number of goal states:", state_space.num_goal_states())
        print()

        self._logger.info("Started generating Aut(G)")
        start_time = time.time()  # Record the start time
        state_graphs = dict()

        num_vertices_dec_graph = 0
        num_vertices_dvc_graph = 0
        max_num_edges_dec_graph = 0
        max_num_edges_dvc_graph = 0
        for state in tqdm(state_space.get_states(), file=sys.stdout):
            state_graph = StateGraph(state)
            state_graphs[state] = state_graph
            max_num_edges_dec_graph = max(max_num_edges_dec_graph, sum([len(edges) for edges in state_graph.dec_graph.adj_list.values()]))
            max_num_edges_dvc_graph = max(max_num_edges_dvc_graph, sum([len(edges) for edges in state_graph.dvc_graph.adj_list.values()]))
            num_vertices_dec_graph = len(state_graph.dec_graph.vertices)
            num_vertices_dvc_graph = len(state_graph.dvc_graph.vertices)

        self._logger.info("Finished generating state graph G")
        end_time = time.time()
        runtime = end_time - start_time
        print(f"Total time: {runtime:.2f} seconds")
        print(f"Total time per state: {runtime / len(state_space.get_states()):.2f} seconds")
        print("Number of vertices in DEC graph:", num_vertices_dec_graph)
        print("Number of vertices in DVC graph:", num_vertices_dvc_graph)
        print("Maximum number of edges in DEC graph:", max_num_edges_dec_graph)
        print("Maximum number of edges in DVC graph:", max_num_edges_dvc_graph)

        equivalence_classes = defaultdict(set)
        for sg1 in state_graphs.values():
            equivalence_classes[sg1.nauty_certificate].add(sg1)
        print("Number of equivalence classes:", len(equivalence_classes))

        if self._dump_dot:
            print("Dumping dot files to \"outputs/\"")
            for class_id, equivalence_class in enumerate(tqdm(equivalence_classes.values(), file=sys.stdout)):
                Path(f"outputs/decs/{class_id}").mkdir(exist_ok=True)
                for i, state_graph in enumerate(equivalence_class):
                    state_graph.dec_graph.to_dot(f"outputs/decs/{class_id}/{i}.gc")
                    state_graph.dvc_graph.to_dot(f"outputs/dvcs/{class_id}/{i}.gc")


    

