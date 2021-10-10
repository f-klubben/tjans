
def string_with_spacing(string: str, spacing: int = 20, offset: int = 0):
    """
    Construct a string with tailing whitespaces for pretty formatting
    :param string: the string to format
    :param spacing: how long the resulting string should be
    :param offset: chars to offset - usually used if the following string is of variable length
    """
    return string + ' ' * (spacing - len(string) + offset)
