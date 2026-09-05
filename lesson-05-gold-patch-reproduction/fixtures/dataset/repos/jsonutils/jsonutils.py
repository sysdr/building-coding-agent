def keys(d):
    return list(d.keys())


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        out[prefix + k] = v
    return out
