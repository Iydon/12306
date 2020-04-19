__all__ = ('station_path', 'train_path')


import os

def same_dir(path, *p):
    '''方便 utils.py 使用路径
    '''
    if not os.path.isdir(path):
        path, _ = os.path.split(path)
    os.makedirs(os.path.join(path, *p[:-1]), exist_ok=True)
    return os.path.join(path, *p)


station_path = same_dir(__file__, 'data', 'stations.csv')
train_path = same_dir(__file__, 'data', 'trains.csv')
