from pymimir import State, Problem
from pynauty import Graph as NautyGraph, certificate as nauty_certificate

from typing import List, MutableSet
from collections import defaultdict

from .color import Color
from .dec_graph import DECVertex, DECEdge, DECGraph
from .dvc_graph import DVCVertex, DVCEdge, DVCGraph
from .uvc_graph import UVCVertex, UVCGraph


class NameToIndexMapper:
    """
    Perfect has function to map a list of types to a color
    """
    def __init__(self):
        self._str_to_int = dict()
        self._int_to_str = dict()

    def add(self, string : str):
        assert string not in self._str_to_int
        number = len(self._str_to_int)
        self._str_to_int[string] = number
        self._int_to_str[number] = string

    def str_to_int(self, string : str):
        assert string in self._str_to_int
        return self._str_to_int[string]

    def int_to_str(self, number : int):
        assert number in self._int_to_str
        return self._int_to_str[number]

    def strs_to_int(self, strings: MutableSet[str]):
        """ Compute a perfect hash value for a given non-empty set of labels.
        """
        assert(strings)
        number = 0
        factor = 1
        for string in sorted(list(strings)):
            number += factor * self._str_to_int[string]
            factor *= len(self._str_to_int)
        return number


class StateGraph:
    """
    In this version, we give all vertices the same color
    and encode type information using loop edges
    """
    def __init__(self, state : State, enable_undirected: bool):
        self._state = state
        # Bookkeeping: create mappings from names to integers
        index_mapper = self._create_index_mapper(state)

        ### Step 1: Create Directed Edge Colored Graph (DECGraph)
        self._dec_graph = self._create_directed_edge_colored_graph(state, index_mapper)

        ### Step 2: Create Directed Vertex Colored Graph (DVCGraph)
        self._dvc_graph = self._create_directed_vertex_colored_graph(self._dec_graph)

        if enable_undirected:
            ### Step 3 B: Translate to pynauty graph
            self._uvc_graph = self._create_undirected_vertex_colored_graph(self._dvc_graph, index_mapper)
            assert self._uvc_graph.test_is_undirected()
            self._nauty_graph = self._create_pynauty_undirected_vertex_colored_graph(self._uvc_graph)
        else:
            ### Step 3 A: Translate to pynauty graph
            self._nauty_graph = self._create_pynauty_directed_vertex_colored_graph(self._dvc_graph)

        ### Step 4: Compute the graph certificate
        self._nauty_certificate = nauty_certificate(self._nauty_graph)

    def _create_index_mapper(self, state: State):
        problem = state.get_problem()
        index_mapper = NameToIndexMapper()
        index_mapper.add(None)  # used to represent "uncolored"
        for obj in problem.objects:
            index_mapper.add("o_" + obj.name)
        for typ in problem.domain.types:
            index_mapper.add("t_" + typ.name)
        for const in problem.domain.constants:
            index_mapper.add("c_" + const.name)
        for pred in problem.domain.predicates:
            index_mapper.add("p_" + pred.name)
            index_mapper.add("p_" + pred.name + "_g")
            index_mapper.add("not p_" + pred.name + "_g")
        return index_mapper

    def _create_directed_edge_colored_graph(self, state : State, index_mapper : NameToIndexMapper):
        problem = state.get_problem()

        # Create empty directed edge colored graph
        graph = DECGraph(state)

        # Add vertices
        for obj in problem.objects:
            v = DECVertex(
                id=index_mapper.str_to_int("o_" + obj.name),
                color=Color(
                    value=index_mapper.str_to_int(None),
                    info=obj.name))
            graph.add_vertex(v)
        for typ in set(obj.type for obj in problem.objects if obj.type.name != "object"):
            v = DECVertex(
                id=index_mapper.str_to_int("t_" + typ.name),
                color=Color(
                    value=index_mapper.str_to_int("t_" + typ.name),
                    info=typ.name))
            graph.add_vertex(v)
        for const in problem.domain.constants:
            v = DECVertex(
                id=index_mapper.str_to_int("c_" + const.name),
                color=Color(
                    value=index_mapper.str_to_int("c_" + const.name),
                    info="constant_" + const.name))
            graph.add_vertex(v)
        for pred in set(atom.predicate for atom in state.get_atoms() if atom.predicate.arity <=1):
            v = DECVertex(
                id=index_mapper.str_to_int("p_" + pred.name),
                color=Color(
                    value=index_mapper.str_to_int("p_" + pred.name),
                    info=pred.name))
            graph.add_vertex(v)
        for pred in set(goal_literal.atom.predicate for goal_literal in problem.goal if goal_literal.atom.predicate.arity <= 1):
            v = DECVertex(
                id=index_mapper.str_to_int("p_" + pred.name + "_g"),
                color=Color(
                    value=index_mapper.str_to_int("p_" + pred.name + "_g"),
                    info=pred.name + "_g"))
            graph.add_vertex(v)

        # Add atom edges
        for dynamic_atom in state.get_atoms():
            if dynamic_atom.predicate.arity == 1:
                v_id = index_mapper.str_to_int("p_" + dynamic_atom.predicate.name)
                v_prime_id = index_mapper.str_to_int("o_" + dynamic_atom.terms[0].name)
                graph.add_edge(DECEdge(v_id, v_prime_id, None))
                graph.add_edge(DECEdge(v_prime_id, v_id, None))
            elif dynamic_atom.predicate.arity == 2:
                if dynamic_atom.predicate.name == "=":
                    # Skip equality
                    continue
                v_id = index_mapper.str_to_int("o_" + dynamic_atom.terms[0].name)
                v_prime_id = index_mapper.str_to_int("o_" + dynamic_atom.terms[1].name)
                graph.add_edge(
                    DECEdge(v_id, v_prime_id,
                        Color(
                            value=index_mapper.str_to_int("p_" + dynamic_atom.predicate.name),
                            info=dynamic_atom.predicate.name)))
            elif dynamic_atom.predicate.arity > 2:
                raise Exception("Got predicate of arity greater than 2! Implementation does not support this.")

        # Add goal atom edges
        for goal_literal in problem.goal:
            if goal_literal.negated:
                raise Exception("Negated goal atoms currently not supported.")
            goal_atom = goal_literal.atom
            predicate_arity = goal_atom.predicate.arity
            predicate_name = goal_atom.predicate.name + "_g"
            if predicate_arity == 1:
                v_id = index_mapper.str_to_int("p_" + predicate_name)
                v_prime_id = index_mapper.str_to_int("o_" + goal_atom.terms[0].name)
                graph.add_edge(DECEdge(v_id, v_prime_id, None))
                graph.add_edge(DECEdge(v_prime_id, v_id, None))
            elif predicate_arity == 2:
                if predicate_name == "=":
                    # Skip equality
                    continue
                v_id = index_mapper.str_to_int("o_" + goal_atom.terms[0].name)
                v_prime_id = index_mapper.str_to_int("o_" + goal_atom.terms[1].name)
                graph.add_edge(
                    DECEdge(v_id, v_prime_id,
                        Color(
                            value=index_mapper.str_to_int("p_" + predicate_name),
                            info=predicate_name)))
            elif predicate_arity > 2:
                raise Exception("Got predicate of arity greater than 2! Implementation does not support this.")

        # Add type edges
        for obj in problem.objects:
            if obj.type.name == "object":  # skip because every PDDL object is of type object
                continue
            v_id = index_mapper.str_to_int("t_" + obj.type.name)
            v_prime_id = index_mapper.str_to_int("o_" + obj.name)
            graph.add_edge(DECEdge(v_id, v_prime_id, None))
            graph.add_edge(DECEdge(v_prime_id, v_id, None))

        # Add constant edges
        for const in problem.domain.constants:
            v_id = index_mapper.str_to_int("c_" + const.name)
            v_prime_id = index_mapper.str_to_int("o_" + const.name)
            graph.add_edge(DECEdge(v_id, v_prime_id, None))
            graph.add_edge(DECEdge(v_prime_id, v_id, None))

        return graph

    def _create_directed_vertex_colored_graph(self, dec_graph: DECGraph):
        ### More compact encoding with loops integrated into vertex colors
        graph = DVCGraph(dec_graph.state)
        next_free_vertex_id = max(vertex.id for vertex in dec_graph.vertices.values()) + 1
        for vertex in dec_graph.vertices.values():
            graph.add_vertex(DVCVertex(
                id=vertex.id,
                color=vertex.color))
        for source_id, edges in dec_graph.adj_list.items():
            # For each transition, encode the label in a helper vertex
            for edge in edges:
                if edge.color is not None:
                    v = dec_graph.vertices[source_id]
                    v_prime = dec_graph.vertices[edge.target_id]
                    v_middle = DVCVertex(next_free_vertex_id, edge.color)
                    next_free_vertex_id += 1
                    graph.add_vertex(v_middle)
                    graph.add_edge(DVCEdge(v.id, v_middle.id))
                    graph.add_edge(DVCEdge(v_middle.id, v_prime.id))
                else:
                    v = dec_graph.vertices[source_id]
                    v_prime = dec_graph.vertices[edge.target_id]
                    graph.add_edge(DVCEdge(v.id, v_prime.id))
        return graph

    def _create_undirected_vertex_colored_graph(self, dvc_graph: DVCGraph, color_mapper: NameToIndexMapper):
        graph = UVCGraph(dvc_graph.state)
        next_free_vertex_id = max(vertex.id for vertex in dvc_graph.vertices.values()) + 1
        for vertex in dvc_graph.vertices.values():
            graph.add_vertex(DVCVertex(
                id=vertex.id,
                color=vertex.color))
        for source_id, edges in dvc_graph.adj_list.items():
            for edge in edges:
                if DVCEdge(edge.target_id, edge.source_id) in dvc_graph.adj_list[edge.target_id]:
                    # There exists an anti-parallel edge
                    v = dvc_graph.vertices[source_id]
                    v_prime = dvc_graph.vertices[edge.target_id]
                    graph.add_edge(v.id, v_prime.id)
                else:
                    # Edge is directed
                    v = dvc_graph.vertices[source_id]
                    v_prime = dvc_graph.vertices[edge.target_id]
                    v_tail_main = DVCVertex(next_free_vertex_id, Color(color_mapper.str_to_int(None)))
                    next_free_vertex_id += 1
                    v_tail_1 = DVCVertex(next_free_vertex_id, Color(color_mapper.str_to_int(None)))
                    next_free_vertex_id += 1
                    v_head_main = DVCVertex(next_free_vertex_id, Color(color_mapper.str_to_int(None)))
                    next_free_vertex_id += 1
                    v_head_1 = DVCVertex(next_free_vertex_id, Color(color_mapper.str_to_int(None)))
                    next_free_vertex_id += 1
                    v_head_2 = DVCVertex(next_free_vertex_id, Color(color_mapper.str_to_int(None)))
                    next_free_vertex_id += 1

                    graph.add_vertex(v_tail_main)
                    graph.add_vertex(v_tail_1)
                    graph.add_vertex(v_head_main)
                    graph.add_vertex(v_head_1)
                    graph.add_vertex(v_head_2)

                    graph.add_edge(v.id, v_tail_main.id)
                    graph.add_edge(v_tail_main.id, v.id)

                    graph.add_edge(v_tail_main.id, v_tail_1.id)
                    graph.add_edge(v_tail_1.id, v_tail_main.id)

                    graph.add_edge(v_tail_main.id, v_head_main.id)
                    graph.add_edge(v_head_main.id, v_tail_main.id)

                    graph.add_edge(v_head_main.id, v_head_1.id)
                    graph.add_edge(v_head_1.id, v_head_main.id)

                    graph.add_edge(v_head_1.id, v_head_2.id)
                    graph.add_edge(v_head_2.id, v_head_1.id)

                    graph.add_edge(v_head_main.id, v_prime.id)
                    graph.add_edge(v_prime.id, v_head_main.id)
        return graph

    def _create_pynauty_undirected_vertex_colored_graph(self, dvc_graph: UVCGraph):
        # remap vertex indices
        old_to_new_vertex_index = dict()
        for vertex in dvc_graph.vertices.values():
            old_to_new_vertex_index[vertex.id] = len(old_to_new_vertex_index)
        adjacency_dict = defaultdict(set)
        for source_id, target_ids in dvc_graph.adj_list.items():
            adjacency_dict[old_to_new_vertex_index[source_id]] = set(old_to_new_vertex_index[target_id] for target_id in target_ids)
        # compute vertex partitioning
        color_to_vertices = defaultdict(set)
        for vertex in dvc_graph.vertices.values():
            color_to_vertices[vertex.color.value].add(old_to_new_vertex_index[vertex.id])
        color_to_vertices = dict(sorted(color_to_vertices.items()))
        vertex_partitioning = list(color_to_vertices.values())

        graph = NautyGraph(
            number_of_vertices=len(old_to_new_vertex_index),
            directed=False,
            adjacency_dict=adjacency_dict,
            vertex_coloring=vertex_partitioning)
        return graph

    def _create_pynauty_directed_vertex_colored_graph(self, dvc_graph: DVCGraph):
        # remap vertex indices
        old_to_new_vertex_index = dict()
        for vertex in dvc_graph.vertices.values():
            old_to_new_vertex_index[vertex.id] = len(old_to_new_vertex_index)
        adjacency_dict = defaultdict(set)
        for source_id, edges in dvc_graph.adj_list.items():
            adjacency_dict[old_to_new_vertex_index[source_id]] = set(old_to_new_vertex_index[edge.target_id] for edge in edges)
        # compute vertex partitioning
        color_to_vertices = defaultdict(set)
        for vertex in dvc_graph.vertices.values():
            color_to_vertices[vertex.color.value].add(old_to_new_vertex_index[vertex.id])
        color_to_vertices = dict(sorted(color_to_vertices.items()))
        vertex_partitioning = list(color_to_vertices.values())

        graph = NautyGraph(
            number_of_vertices=len(old_to_new_vertex_index),
            directed=True,
            adjacency_dict=adjacency_dict,
            vertex_coloring=vertex_partitioning)
        return graph

    def __str__(self):
        return f"StateGraph({str(self._dec_graph)})"

    @property
    def state(self):
        return self._state

    @property
    def dec_graph(self):
        return self._dec_graph

    @property
    def dvc_graph(self):
        return self._dvc_graph

    @property
    def uvc_graph(self):
        return self._uvc_graph

    @property
    def nauty_certificate(self):
        return self._nauty_certificate
