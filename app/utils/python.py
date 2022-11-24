def ensure_list(el_or_list):
    if isinstance(el_or_list, list):
        return el_or_list
    return [el_or_list]
