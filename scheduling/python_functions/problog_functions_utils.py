import re


def reformat_problog_predicates(predicates: list) -> str|tuple :
    """
    Reformats predicates read from problog files.

    :param predicates: The predicates to reformat.
    :return: The reformatted predicates.
    """

    formatted_predicates = []
    for predicate in predicates:
        predicate_cleaned = re.match("\'(.*?)\'", predicate)
        if predicate_cleaned is not None:
            formatted_predicates.append(predicate_cleaned.group(1))
        else:
            formatted_predicates.append(predicate)

    return tuple(formatted_predicates) if len(formatted_predicates) > 1 else formatted_predicates[0]