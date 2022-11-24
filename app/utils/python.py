def ensure_list(el_or_list):
    if isinstance(el_or_list, list):
        return el_or_list
    return [el_or_list]


def ensure_1D_list(el_or_list):
    l = ensure_list(el_or_list)
    new_l = []
    for el in l:
        if isinstance(el, list):
            new_l += ensure_1D_list(el)
        else:
            new_l += [el]
    return new_l
