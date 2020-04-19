__all__ = ('constid_path', )


import os


def same_dir(path, *p):
    if not os.path.isdir(path):
        path, _ = os.path.split(path)
    os.makedirs(os.path.join(path, *p[:-1]), exist_ok=True)
    return os.path.join(path, *p)


constid_path = same_dir(__file__, 'constid.txt')
