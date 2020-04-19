'''Download data from 12306

TODO:
    - collect all configurations

Reference:
    - https://github.com/metromancn/Parse12306
'''

__all__ = ('stations', 'trains')


import json
import os
import pandas as pd
import requests


data_dir = '/data/12306'
station_path = os.path.join(data_dir, 'stations.csv')
train_path = os.path.join(data_dir, 'trains.csv')


def load_stations(path=None):
    '''从12306下载车站信息

    Argument:
        - path: str, NoneType
    '''
    if isinstance(path, str) and os.path.exists(path):
        print('Loading off-line...')
        return pd.read_csv(path, index_col=None)
    else:
        print('Loading on-line...')
        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        headers = ['拼音码', '站名', '电报码', '拼音', '首字母', 'ID']
        text = requests.get(url).text
        lines= text[text.index("'")+1: text.rindex("'")]
        data = [line.split('|') for line in lines.split('@') if line]
        df = pd.DataFrame(data, columns=headers)
        del df['ID']
        if isinstance(path, str):
            df.to_csv(path, index=False)
        return df


def load_trains(path=None):
    '''从12306下载车次信息

    Argument:
        - path: str, NoneType
    '''
    if isinstance(path, str) and os.path.exists(path):
        print('Loading off-line...')
    else:
        print('Loading on-line...')
        url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js'
        text = requests.get(url).text
        data = json.loads(text[text.index('{'): text.rindex('}')+1])
        return data


stations = load_stations(station_path)
trains = load_trains(None)
