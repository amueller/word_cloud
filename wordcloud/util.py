def isstr(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)
