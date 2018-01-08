import re


def fetch_version(text):
    """
    >>> fetch_version('234_aaaaa_only_bbb_cc')
    (234,)
    """
    text = text.split('.')[0].lower()
    r = re.match('^([0-9]+)_', text)
    if not r:
        return None
    version = int(r.groups()[0])
    onlys = excepts = None
    if '_only_' in text:
        onlys = text.split('_only_', 1)[-1].split('_')
    elif '_except_' in text:
        excepts = text.split('_except_', 1)[-1].split('_')
    else:
        excepts = []
    return version, onlys, excepts
