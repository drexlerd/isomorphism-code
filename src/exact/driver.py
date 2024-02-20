import time

from . import logger

from pathlib import Path
from collections import defaultdict

from pymimir import *

from ..state_graph import StateGraph


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        logger.setLevel(verbosity)


    def run(self):
        logger.info("Started generating state graph G")
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

        logger.info("Started generating Aut(G)")
        start_time = time.time()  # Record the start time
        state_graphs = dict()
        for i, state in enumerate(state_space.get_states()):
            if (i % 10 == 0):
                logger.info(f"Created certificate for {i}/{len(state_space.get_states())}")
            state_graph = StateGraph(state)
            #state_graph.dec_graph.to_dot()
            state_graph.dvc_graph.to_dot()
            state_graphs[state] = state_graph
            
            break

        abstract_states = defaultdict(set)
        count = 0
        for sg1 in state_graphs.values():
            abstract_states[sg1.nauty_certificate] = sg1.state
            for sg2 in state_graphs.values():
                if sg1.nauty_certificate == sg2.nauty_certificate:
                    count += 1
        print("Fraction of pairwise isomorphic states:", count / (len(state_graphs) ** 2))
        print("Abstraction size:", len(abstract_states))

        logger.info("Finished generating state graph G")
        end_time = time.time() 
        runtime = end_time - start_time
        print(f"Total runtime: {runtime:.2f} seconds")

