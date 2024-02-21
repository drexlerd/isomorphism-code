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
        self._logger.info("Started generating state graph G")
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)

        domain_parser = DomainParser(str(self._domain_file_path))
        domain = domain_parser.parse()
        problem_parser = ProblemParser(str(self._problem_file_path))
        problem = problem_parser.parse(domain)

        state_space = StateSpace.new(problem, LiftedSuccessorGenerator(problem))
        print("Num states:", state_space.num_states())
        print("Num transitions:", state_space.num_transitions())
        print("Num deadend states:", state_space.num_dead_end_states())
        print("Num goal states:", state_space.num_goal_states())

        self._logger.info("Started generating Aut(G)")
        start_time = time.time()  # Record the start time
        state_graphs = dict()

        for state in tqdm(state_space.get_states()):
            state_graph = StateGraph(state)
            state_graphs[state] = state_graph

        self._logger.info("Finished generating state graph G")
        end_time = time.time() 
        runtime = end_time - start_time
        print(f"Total runtime: {runtime:.2f} seconds")

        equivalence_classes = defaultdict(set)
        for sg1 in state_graphs.values():
            equivalence_classes[sg1.nauty_certificate].add(sg1)
        print("Number of equivalence classes:", len(equivalence_classes))

        if self._dump_dot:
            print("Dumping dot files to \"outputs/\"")
            for class_id, equivalence_class in enumerate(tqdm(equivalence_classes.values())):
                Path(f"outputs/decs/{class_id}").mkdir(exist_ok=True)
                for i, state_graph in enumerate(equivalence_class):
                    state_graph.dec_graph.to_dot(f"outputs/decs/{class_id}/{i}.gc")
                    state_graph.dvc_graph.to_dot(f"outputs/dvcs/{class_id}/{i}.gc")


    

