__all__ = ('lazy_property', 'load_stations', 'load_trains')


import json
import os
import pandas as pd
import re
import requests

from .config import station_path, train_path


def lazy_property(func):
    '''Lazy property

    References
    =======
    (Python Cookbook)[https://python3-cookbook.readthedocs.io/zh_CN/latest/c08/p10_using_lazily_computed_properties.html]

    Example
    =======
        >>> import math
        >>> class Circle:
        ... 	def __init__(self, radius):
        ... 		self.radius = radius
        ... 	@lazy_property
        ... 	def area(self):
        ... 		print('Computing area')
        ... 		return math.pi * self.radius**2
    '''
    name = '_lazy_' + func.__name__
    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy


def load_stations(path=station_path, update=False):
    '''从 12306 下载车站信息

    Argument:
        - path: str, NoneType
        - update: bool
    '''
    if not update and isinstance(path, str) and os.path.exists(path):
        return pd.read_csv(path, index_col=None)
    else:
        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        headers = ['拼音码', '站名', '电报码', '拼音', '首字母', 'ID']
        text = requests.get(url).text
        lines= text[text.index("'")+1: text.rindex("'")]
        data = tuple(line.split('|') for line in lines.split('@') if line)
        df = pd.DataFrame(data, columns=headers)
        del df['ID']
        if isinstance(path, str):
            df.to_csv(path, index=False)
        return df


def load_trains(path=train_path, update=False):
    '''从 12306 下载车次信息

    Argument:
        - path: str, NoneType
        - update: bool
    '''
    def iterrows(data):
        # ('时间', '类型', '列车编号', '车次', '起点', '终点')
        pattern = re.compile(r'[^()-]+')
        for time, subdata in data.items():
            for key, vals in subdata.items():
                for val in vals:
                    x = pattern.findall(val['station_train_code'])
                    yield time, key, val['train_no'], *x

    if not update and isinstance(path, str) and os.path.exists(path):
        return pd.read_csv(path, index_col=None)
    else:
        url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js'
        headers = ['时间', '类型', '列车编号', '车次', '起点', '终点']
        text = requests.get(url).text
        data = json.loads(text[text.index('{'): text.rindex('}')+1])
        df =  pd.DataFrame(tuple(iterrows(data)), columns=headers)
        if isinstance(path, str):
            df.to_csv(path, index=False)
        return df
