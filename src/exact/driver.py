from . import logger

from pathlib import Path

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

        state_graphs = dict()
        for state in state_space.get_states():
            state_graph = StateGraph(state)
            state_graph.dec_graph.to_dot()
            state_graph.dvc_graph.to_dot()
            state_graphs[state] = state_graph
            break

        logger.info("Started generating Aut(G)")

