
from pymimir import Domain


class ColorFunction:
    def __init__(self, domain: Domain):
        """ Initialize a canonical planning domain labelling.
        """
        # Make the labelling canonical with respect to predicate and type names
        self._domain_label_to_color = dict()
        for typ in sorted(domain.types, key = lambda x: x.name):
            self._domain_label_to_color[typ.name] = len(self._domain_label_to_color)
        for predicate in sorted(domain.predicates, key = lambda x : x.name):
            for pos in range(len(predicate.parameters)):
                self._domain_label_to_color[(predicate.name, pos)] = len(self._domain_label_to_color)
                self._domain_label_to_color[(predicate.name + "_g", pos)] = len(self._domain_label_to_color)

        self._aggregate_to_color = dict()

    def get_color_from_domain_label(self, key):
        """ Return a preset color for a given label

        The key must be present, or otherwise,
        we have not properly initialzed a canonical labelling for the domain
        """
        assert key in self._domain_label_to_color
        return self._domain_label_to_color[key]

    def get_color_from_aggregate_label(self, key):
        """ Return the color of an aggregate
        """
        if key not in self._aggregate_to_color:
            self._aggregate_to_color[key] = len(self._domain_label_to_color) + len(self._aggregate_to_color)
        return self._aggregate_to_color[key]


