
from pymimir import Domain


class ColorFunction:
    def __init__(self, domain: Domain):
        """ Initialize a canonical planning domain labelling.
        """
        # Make the labelling canonical with respect to predicate and type names
        self._domain_label_to_color = dict()
        for predicate in sorted(domain.get_fluent_predicates() + domain.get_static_predicates(), key = lambda x : x.get_name()):
            for pos in range(len(predicate.get_parameters())):
                self._domain_label_to_color[(predicate.get_name(), pos)] = len(self._domain_label_to_color)
                self._domain_label_to_color[(predicate.get_name() + "_g", pos)] = len(self._domain_label_to_color)
            if len(predicate.get_parameters()) == 0:
                self._domain_label_to_color[(predicate.get_name(), -1)] = len(self._domain_label_to_color)
                self._domain_label_to_color[(predicate.get_name() + "_g", -1)] = len(self._domain_label_to_color)

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


