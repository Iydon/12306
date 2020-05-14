'''
Example:
    - 1
        >>> from data import load_stations, load_trains
        >>> stations = load_stations()
        >>> trains = load_trains()
    - 2
        >>> from ly import Train
        >>> t = Train()
'''

from ly import Train


t = Train()

stations = t.stations
tickets = t.remainder_tickets('北京西', '济南东', '2020-05-04')
stop_overs = t.stop_overs('北京', '成都', 'G89', '2020-05-23')
