import string

WILDCARD = '#'


def replace_nonprintable(s):
    if isinstance(s, str):
        return ''.join([x if x in string.printable else WILDCARD for x in s])
    return None
