from collections.abc import Iterable
import math

def depth(l):
    if type(l) is dict and l:
        return 1 + max(depth(l[el]) for el in l)
    if type(l) is list and l:
        return 1 + max(depth(el) for el in l)
    return 0

def flatten(l, max_depth=math.inf):
    if isinstance(l, dict):
        if max_depth > 0:
            yield from flatten(l.values(), max_depth - 1)
        else:
            yield l
    else:
        if max_depth > 0:
            for el in l:
                if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
                    yield from flatten(el, max_depth - 1)
                else:
                    yield el
        else:
            yield l


def roman_to_arabic(n: str):
    """ Convert a Roman numeral to an Arabic integer. """

    if isinstance(n, str):
        n = n.upper()
        numerals = {'M': 1000,
                    'D': 500,
                    'C': 100,
                    'L': 50,
                    'X': 10,
                    'V': 5,
                    'I': 1
                    }
        sum = 0
        for i in range(len(n)):
            try:
                value = numerals[n[i]]
                if i+1 < len(n) and numerals[n[i+1]] > value:
                    sum -= value
                else:
                    sum += value
            except KeyError:
                return None
        return sum
