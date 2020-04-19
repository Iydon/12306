__all__ = ('Train', )



import collections
import json
import requests
import time

from selenium import webdriver

from .config import constid_path
from .utils import lazy_property



Station = collections.namedtuple('Station', ('hot', 'priority', 'match', 'quanpin'))
Ticket = collections.namedtuple(
    'Ticket', (
        'from_city', 'to_city', 'train_number', 'date', 'from_time', 'to_time', 'used_minutes',
        'from_station', 'to_station', 'seats', 'from_type', 'to_type', 'if_book', 'is_book',
        'priority', 'sort', 'both_mile', 'train_id', 'flag', 'flag_message', 'sale_flag',
    )
)
Seat = collections.namedtuple('Seat', ('name', 'price', 'up', 'mid', 'down'))
StopOver = collections.namedtuple('StopOver', ('name', 'start_time', 'end_time', 'over_time'))



class Train:
    '''同程旅游火车票模型
    '''

    def __init__(self, browser='Firefox'):
        with open(constid_path, 'r') as f:
            self._constid = f.read().strip()
        self._browser = browser


    @lazy_property
    def stations(self):
        '''返回所有的城市（火车站）
        '''
        url = 'https://www.ly.com/uniontrain/trainapi/TrainPCCommon/GetAllCity'
        params = dict(
            headct=0, platId=1, headver='1.0.0', headtime=self.headtime, memberId=0,
        )
        result = dict()
        response = requests.get(url, params=dict(para=json.dumps(params)))
        for city, data in response.json()['data'].items():
            h, p, q = data['hot'], data['priority'], data['quanpin']
            result[city.replace(' ', '')] = Station(h, p, data['match'].split('|'), q)
        return result


    @property
    def headtime(self):
        return int(1000*time.time())


    def remainder_tickets(self, from_, to, date, sort_by='fromTime'):
        '''余票信息

        Example:
            >>> t = Train()
            >>> t.remainder_tickets('北京西', '济南东', '2020-05-04')
        '''
        def yield_tickets(data):
            fc, tc = data['fromCityName'], data['toCityName']
            date = data['trainDate']
            for train in data['trains']:
                seats = tuple(
                    Seat(t['cn'], float(t['price']), t['upPrice'], t['midPrice'], t['downPrice'])
                    for t in train['ticketState'].values()
                )
                yield Ticket(
                    fc, tc, train['trainNum'], date, train['fromTime'], train['toTime'],
                    train['usedTimeInt'], train['beginPlace'], train['endPlace'],
                    seats, train['fromType'], train['toType'], train['ifBook'],
                    train['isBook'], train['priority'], train['sort'], train['bothMile'],
                    train['trainId'], train['trainFlag'], train['trainFlagMsg'], train['saleFlag'],
                )

        url = 'https://www.ly.com/uniontrain/trainapi/TrainPCCommon/SearchTrainRemainderTickets'
        params = dict(
            To=to, From=from_, TrainDate=date, SortBy=sort_by, constId=self._constid,
            headtime=self.headtime, memberId=0, headct=0, platId=1, headver='1.0.0',
            PassType='', TrainClass='', FromTimeSlot='', ToTimeSlot='', FromStation='',
            ToStation='', callback='', tag='',
        )
        response = requests.get(url, params=dict(para=json.dumps(params)))
        return tuple(yield_tickets(response.json()['data']))


    def stop_overs(self, from_, to, train_num, date):
        '''中转站信息

        Example:
            >>> t = Train()
            >>> t.stop_overs('北京', '成都', 'G89', '2020-05-23')
        '''
        def yield_stop_overs(data):
            for station in data:
                keys = ('stationName', 'startTime', 'endTime', 'overTime')
                yield StopOver(*(station[key] for key in keys))

        url = 'https://www.ly.com/uniontrain/trainapi/Station/GetStopOvers'
        params = {
            'from': from_, 'to': to, 'trainnum': train_num, 'querydate': date.replace('-', ''),
            'headct': 0, 'platId': 1, 'headver': '1.0.0', 'headtime': self.headtime, 'memberId': 0,
        }
        response = requests.get(url, params=dict(para=json.dumps(params)))
        data = response.json()['data']['stopOvers']  # ['stopOvers', 'depStatNo', 'arrStatNo']
        return tuple(yield_stop_overs(data))


    def update_constid(self):
        if isinstance(self._browser, str):
            self._browser = getattr(webdriver, self._browser)()
        url = 'https://www.ly.com/huochepiao/Pages/Search.aspx?FromStation=beijing&ToStation=shanghai'
        id = 'header'
        js = f'document.getElementById("{id}").innerText = _dx.Suuid;'
        self._browser.get(url)
        self._browser.execute_script(js)
        self._constid = self._browser.find_element_by_id(id).text
        with open(constid_path, 'w') as f:
            f.write(self._constid)
