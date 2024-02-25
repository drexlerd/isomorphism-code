import sys
import time

from pathlib import Path
from collections import defaultdict, deque

from pymimir import DomainParser, ProblemParser, StateSpace, LiftedSuccessorGenerator, GroundedSuccessorGenerator
from tqdm import tqdm

from .state_graph import StateGraph
from .equivalence_graph import EquivalenceGraph as XEquivalenceGraph, \
    Object as XObject, \
    Constant as XConstant, \
    Predicate as XPredicate, \
    Atom as XAtom, \
    Literal as XLiteral, \
    Domain as XDomain, \
    Problem as XProblem, \
    State as XState, \
    Action as XAction, \
    Transition as XTransition
from .logger import initialize_logger, add_console_handler
from .search_node import SearchNode


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, dump_dot: bool, enable_pruning: bool, dump_equivalence_graph: bool, enable_undirected: bool, debug: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._dump_dot = dump_dot
        self._enable_pruning = enable_pruning
        self._dump_equivalence_graph = dump_equivalence_graph
        self._enable_undirected = enable_undirected
        self._debug = debug
        self._logger = initialize_logger("exact")
        self._logger.setLevel(verbosity)
        add_console_handler(self._logger)

    def run(self):
        """ Main loop for computing Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

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
        search_nodes[initial_state] = SearchNode(None, None)
        num_generated_states += 1

        while queue:
            cur_state = queue.popleft()

            state_graph = StateGraph(cur_state, self._enable_undirected)

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
                search_nodes[suc_state] = SearchNode(cur_state, applicable_action)

                num_generated_states += 1

                queue.append(suc_state)
        print()

        end_time = time.time()
        runtime = end_time - start_time
        self._logger.info("Finished generating Aut(G)")
        print(f"Total time: {runtime:.2f} seconds")
        print("Number of generated states:", num_generated_states)
        print("Number of equivalence classes:", len(equivalence_classes))
        print("Number of vertices in DEC graph:", max(max(len(state_graph.dec_graph.vertices) for state_graph in state_graphs) for state_graphs in equivalence_classes.values()))
        print("Number of vertices in DVC graph:", max(max(len(state_graph.dvc_graph.vertices) for state_graph in state_graphs) for state_graphs in equivalence_classes.values()))
        if self._enable_undirected:
            print("Number of vertices in UVC graph:", max(max(len(state_graph.uvc_graph.vertices) for state_graph in state_graphs) for state_graphs in equivalence_classes.values()))
        print()

        if self._dump_dot:
            print("Dumping dot files to \"outputs/\"")
            for class_id, state_graphs in enumerate(tqdm(equivalence_classes.values(), file=sys.stdout)):
                for i, state_graph in enumerate(state_graphs):
                    state_graph.dec_graph.to_dot(f"outputs/decs/{class_id}/{i}.gc")
                    state_graph.dvc_graph.to_dot(f"outputs/dvcs/{class_id}/{i}.gc")
                    if self._enable_undirected:
                        state_graph.uvc_graph.to_dot(f"outputs/uvcs/{class_id}/{i}.gc")

        if self._dump_equivalence_graph:
            constant_map = {const : XConstant(const.name) for const in domain.constants}
            object_map = {obj: XObject(obj.name) for obj in problem.objects}
            predicate_map = {pred: XPredicate(pred.name, pred.arity) for pred in domain.predicates}
            static_predicate_map = {pred: XPredicate(pred.name, pred.arity) for pred in domain.static_predicates}
            encountered_atom_map = {atom: XAtom(predicate_map[atom.predicate], [object_map[obj] for obj in atom.terms]) for atom in problem.get_encountered_atoms()}
            goal_literal_map = {literal: XLiteral(XAtom(predicate_map[literal.atom.predicate], [object_map[obj] for obj in literal.atom.terms]), literal.negated) for literal in problem.goal}
            state_map = {state: index for index, state in enumerate(closed_list)}
            states = {
                state_map[state_graph.state]: XState(
                    state_map[state_graph.state],
                    [encountered_atom_map[atom] for atom in state_graph.state.get_static_atoms()],
                    [encountered_atom_map[atom] for atom in state_graph.state.get_fluent_atoms()],
                    class_id
                )
                for class_id, state_graphs in enumerate(equivalence_classes.values())
                for state_graph in state_graphs
            }
            transitions = defaultdict(list)
            for target_id, state in enumerate(closed_list):
                if search_nodes[state].parent_state is not None:
                    source_id = state_map[search_nodes[state].parent_state]
                    transitions[source_id].append(XTransition(source_id, target_id, XAction(search_nodes[state].creating_action.schema.name, [object_map[obj] for obj in search_nodes[state].creating_action.get_arguments()])))
            domain = XDomain(list(constant_map.values()), list(predicate_map.values()), list(static_predicate_map.values()))
            problem = XProblem(list(encountered_atom_map.values()), list(goal_literal_map.values()))
            graph = XEquivalenceGraph(domain, problem, states, transitions)
            graph.write(Path("equivalence_graph.json").absolute())
            # graph.read(Path("equivalence_graph.json").absolute())
