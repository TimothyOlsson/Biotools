def fix_list(a_list, html=False):
    """Takes a list and returns a stringyfied list with \n"""
    a_list = [str(x) for x in a_list]
    if html:
        a_list = '<br/>'.join(a_list)
    else:
        a_list = '\n'.join(a_list)
    return a_list
