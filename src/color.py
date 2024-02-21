

class Color:
    """ A color is just an integer with attached meaning for interpretation.
    """
    def __init__(self, abstract: int, concrete: str):
        self._abstract = abstract
        self._concrete = concrete

    def __eq__(self, other : "Color"):
        return self._abstract == other._abstract

    def __hash__(self):
        return hash(self._abstract)
    
    def __str__(self):
        return f"{self._abstract}:{self._concrete}"

    @property 
    def abstract(self):
        return self._abstract
    
    @property
    def concrete(self):
        return self._concrete
    