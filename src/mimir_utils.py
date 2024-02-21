from pymimir import Type


def flatten_types(type : Type):
    """ Flatten the type hierarchy into a list for a given type.
    """
    result_types = []

    cur_type = type
    while cur_type != None:
        if (cur_type.base is not None):
            result_types.append(cur_type.base)
        cur_type = cur_type.base

    return result_types
