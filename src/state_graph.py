from pymimir import State
from pynauty import Graph as NautyGraph, certificate as nauty_certificate

from typing import List, MutableSet
from collections import defaultdict

from .color import Color
from .dec_graph import DECVertex, DECEdge, DECGraph
from .dvc_graph import DVCVertex, DVCEdge, DVCGraph


class StringToIntMapper:
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
        return self._str_to_int[string]

    def int_to_str(self, number : int):
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
    def __init__(self, state : State):
        # Store the state for reference
        self._state = state

        # Bookkeeping
        problem = state.get_problem()
        vertex_mapper = StringToIntMapper()
        for obj in problem.objects:
            vertex_mapper.add(obj.name)
        color_mapper = StringToIntMapper()
        for typ in problem.domain.types:
            color_mapper.add(typ.name)
        for pred in problem.domain.predicates:
            color_mapper.add(pred.name)
            color_mapper.add(pred.name + "_g")
        for const in problem.domain.constants:
            color_mapper.add(const.name)


        ### Step 1: Create Directed Edge Colored Graph (DECGraph)

        # Create empty directed edge colored graph
        self._dec_graph = DECGraph(state)

        # Add vertices
        for obj in problem.objects:
            # Create color based on the type
            # Note: we currently assume that each object has a single parent type
            # To support "either" types, we must compute an aggregate
            v = DECVertex(id=vertex_mapper.str_to_int(obj.name), color=Color(color_mapper.str_to_int(obj.type.name), obj.name))
            self._dec_graph.add_vertex(v)

        # Add atom edges 
        for dynamic_atom in state.get_atoms():
            if dynamic_atom.predicate.arity > 2:
                raise Exception("Got predicate of arity 2! Implementation does not support this.")
            if dynamic_atom.predicate.arity == 1:
                v_id = vertex_mapper.str_to_int(dynamic_atom.terms[0].name)
                self._dec_graph.add_edge(DECEdge(v_id, v_id, Color(color_mapper.str_to_int(dynamic_atom.predicate.name), dynamic_atom.predicate.name)))
            if dynamic_atom.predicate.arity == 2:
                if dynamic_atom.predicate.name == "=":
                    # Skip equality
                    continue
                v_id = vertex_mapper.str_to_int(dynamic_atom.terms[0].name)
                v_prime_id = vertex_mapper.str_to_int(dynamic_atom.terms[1].name)
                self._dec_graph.add_edge(DECEdge(v_id, v_prime_id, Color(color_mapper.str_to_int(dynamic_atom.predicate.name), dynamic_atom.predicate.name)))

        # Add goal atom edges
        for goal_literal in problem.goal:
            if goal_literal.negated:
                raise Exception("Negated goal atoms currently not supported.")
            goal_atom = goal_literal.atom
            predicate_arity = goal_atom.predicate.arity
            predicate_name = goal_atom.predicate.name + "_g"
            if predicate_arity > 2:
                raise Exception("Got predicate of arity 2! Implementation does not support this.")
            if predicate_arity == 1:
                v = DECVertex(
                    id=vertex_mapper.str_to_int(goal_atom.terms[0].name), 
                    color=Color(color_mapper.str_to_int(goal_atom.terms[0].type.name), goal_atom.terms[0].name))
                self._dec_graph.add_edge(DECEdge(v, v, Color(color_mapper.str_to_int(predicate_name), predicate_name)))
            if predicate_arity == 2:
                if predicate_name == "=":
                    # Skip equality
                    continue
                v_id = vertex_mapper.str_to_int(goal_atom.terms[0].name)
                v_prime_id = vertex_mapper.str_to_int(goal_atom.terms[1].name)
                self._dec_graph.add_edge(DECEdge(v_id, v_prime_id, Color(color_mapper.str_to_int(predicate_name), predicate_name)))

        # Add constant edges
        for const in problem.domain.constants:
            const_name = const.name
            v_id = vertex_mapper.str_to_int(const_name)
            self._dec_graph.add_edge(DECEdge(v_id, v_id, Color(color_mapper.str_to_int(const_name), const_name)))


        ### Step 2: Create Directed Vertex Colored Graph (DVCGraph)
            
        ### More compact encoding with loops integrated into vertex colors
        self._dvc_graph = DVCGraph(state)
        for vertex in self._dec_graph.vertices.values():
            self._dvc_graph.add_vertex(DVCVertex(vertex.id, vertex.color))
        for _, edges in self._dec_graph.adj_list.items():
            for edge in edges:
                v = DVCVertex(edge.source_id, self._dec_graph.vertices[edge.source_id].color)
                v_middle = DVCVertex(len(self.dvc_graph.vertices), edge.color)
                v_prime = DVCVertex(edge.target_id, self._dec_graph.vertices[edge.target_id].color)
                self.dvc_graph.add_vertex(v_middle)
                self.dvc_graph.add_edge(DVCEdge(v, v_middle))
                self.dvc_graph.add_edge(DVCEdge(v_middle, v_prime))


        ### Step 3: Translate to pynauty graph
                
        color_to_vertices = defaultdict(set)
        for vertex in self._dvc_graph.vertices:
            color_to_vertices[vertex.color.abstract].add(vertex.id)
        color_to_vertices = dict(sorted(color_to_vertices.items()))
        vertex_partitioning = [vertex_ids for vertex_ids in color_to_vertices.values()]
        self._nauty_graph = NautyGraph(
            number_of_vertices=len(self._dvc_graph.vertices),
            directed=True,
            adjacency_dict={source.id: [edge.target.id for edge in edges] for source, edges in self._dvc_graph.adj_list.items()},
            vertex_coloring=vertex_partitioning)
        self._nauty_certificate = nauty_certificate(self._nauty_graph)


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
    def nauty_certificate(self):
        return self._nauty_certificate
