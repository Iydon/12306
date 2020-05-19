__all__ = ('constid_path', 'station_path', 'train_path')


import os


def same_dir(path, *p):
    if not os.path.isdir(path):
        path, _ = os.path.split(path)
    os.makedirs(os.path.join(path, *p[:-1]), exist_ok=True)
    return os.path.join(path, *p)


constid_path = same_dir(__file__, 'constid.txt')
station_path = same_dir(__file__, 'data', 'stations.csv')
train_path = same_dir(__file__, 'data', 'trains.csv')
