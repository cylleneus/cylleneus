from datetime import datetime
import math
import unicodedata
import re
import sys
from collections import Iterable, Mapping
from itertools import chain, zip_longest
from lxml.etree import tostring


DEBUG_OFF = 0
DEBUG_LOW = 1
DEBUG_MEDIUM = 2
DEBUG_HIGH = 3


def print_debug(level, msg, out=sys.stderr):
    from settings import DEBUG

    if level <= DEBUG:
        out.write("%s%s\n" % (" " * level, msg))


def stringify(node):
    from html import unescape

    parts = (
            list(
                chain(
                    *([str(tostring(c))]
                      for c in node.getchildren())
                )
            )
    )
    s = ''.join(filter(None, parts))
    s = re.sub(r"^b\'(.*?)\'$", r'\1', s, flags=re.DOTALL)
    subs = [r'\\[fnrtv]', r'<.*?>', r'</.*?>']
    for sub in subs:
        s = re.sub(sub, r'', s)
    return unescape(s)


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', re.sub(r'[:=]', '-', value).strip().lower())
    return re.sub(r'[\s]+', '-', value)


def dtformat(dt):
    """Converts a datetime object to more human-readable format."""

    D = str(datetime.now() - dt)
    if D.find(',') > 0:
        days, hours = D.split(',')
        days = int(days.split()[0].strip())
        hours, minutes = hours.split(':')[0:2]
    else:
        hours, minutes = D.split(':')[0:2]
        days = 0
    days, hours, minutes = int(days), int(hours), int(minutes)
    datelets =[]
    years, months, xdays = None, None, None
    plural = lambda x: 's' if x != 1 else ''
    if days >= 365:
        years = days // 365
        datelets.append('%d year%s' % (years, plural(years)))
        days = days % 365
    if days >= 30 and days < 365:
        months = days // 30
        datelets.append('%d month%s' % (months, plural(months)))
        days = days % 30
    if not years and days > 0 and days < 30:
        xdays = days
        datelets.append('%d day%s' % (xdays, plural(xdays)))
    if not (months or years) and hours != 0:
        datelets.append('%d hour%s' % (hours, plural(hours)))
    if not (xdays or months or years):
        datelets.append('%d minute%s' % (minutes, plural(minutes)))
    return ', '.join(datelets) + ' ago'


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


def nrange(start, end, zeroes=True):
    start, end = zip(*zip_longest(start, end, fillvalue=0))
    base = max(max(chain(start, end)), 9) + 1

    def _toint(seq, base):
        return sum(base ** n * val for n, val in enumerate(reversed(seq)))

    def _totuple(num, base, length):
        ret = []
        for n in (base ** i for i in reversed(range(length))):
            res, num = divmod(num, n)
            ret.append(res)
        return tuple(ret)

    for se in range(_toint(start, base), _toint(end, base) + 1):
        t = _totuple(se, base, len(start))
        if not zeroes:
            if 0 not in t:
                yield t
        else:
            yield t


# Hashable dict
class hdict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def nested_dict_iter(nested, path=None):
    if not path:
        path = []
    for i in nested.keys():
        local_path = path[:]
        local_path.append(i)
        if isinstance(nested[i], Mapping):
            yield from nested_dict_iter(nested[i], local_path)
        else:
            yield local_path, nested[i]


def matchcase(word):
    def replace(m):
        text = m.group()
        if text.isupper():
            return word.upper()
        elif text.islower():
            return word.lower()
        elif text[0].isupper():
            return word.capitalize()
        else:
            return word
    return replace
