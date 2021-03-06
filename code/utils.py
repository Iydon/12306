from collections import Counter
from datetime import date, datetime
from enum import Enum
from warnings import warn

try:
    from .database import (
        Admin, User, City, Order, Station, Journey, SeatType, Capacity, Ticket,
        session,
    )
    from .config import is_cached, residence_seconds
except:
    from database import (
        Admin, User, City, Order, Station, Journey, SeatType, Capacity, Ticket,
        session,
    )
    from config import is_cached, residence_seconds


status = Enum('status', ('booked', 'paid', 'canceled'))


class Cache:
    '''数据缓存
    '''
    def __init__(self, is_cached):
        self.is_cached = is_cached

    @property
    def stations(self):
        return self._api('station', get.stations)

    @property
    def cities(self):
        return self._api('cities', get.cities)

    @property
    def provinces(self):
        return self._api('provinces', get.provinces)

    @property
    def train_numbers(self):
        return self._api('train_numbers', get.train_numbers)

    def has_train_number(self, train_number):
        if self.is_cached:
            return train_number in self.train_numbers
        return get._by(Journey, train_number=train_number, is_valid=True) is not None

    def update(self):
        for key in tuple(self.__dict__.keys()):
            if key.startswith('_'):
                delattr(self, key)

    def _api(self, name, function, *args, **kwargs):
        if self.is_cached:
            attr = getattr(self, f'_{name}', None)
            if not attr:
                attr = function(*args, **kwargs)
                setattr(self, f'_{name}', attr)
            return attr
        return function(*args, **kwargs)

cache = Cache(is_cached)


class update:
    '''更新数据
    '''
    @classmethod
    def cache(cls):
        cache.update()

    @classmethod
    def orders(cls):
        '''加锁（read）
        '''
        now = datetime.now()
        for order in get._by(Order, status=status.booked.value, iter=True, lock='read'):
            if (now - order.create_date).seconds > residence_seconds:
                order.status = status.canceled.value

    @classmethod
    def train(cls, train_number, carriage_index, seat_type=None, seat_num=None):
        '''
        Argument:
            - train_number: str
            - carriage_index: int
            - seat_type: int, in [1, 18]
            - seat_num: int
        '''
        carriage = get._by(Capacity, train_number=train_number, carriage_index=carriage_index, is_valid=True)
        if seat_type is not None:
            assert get._by(SeatType, id=seat_type) is not None
            carriage.seat_type = seat_type
        if seat_num is not None:
            carriage.seat_num = seat_num
        cls._commit()

    @classmethod
    def station(cls, name, city_name_or_id=None, is_valid=None):
        '''
        Argument:
            - name: str
            - city_name_or_id: NoneType or str or int
            - is_valid: NoneType or bool
        '''
        station = get._by(Station, name=name)
        if city_name_or_id is not None:
            if isinstance(city_name_or_id, str):
                city_name_or_id, = get._by(City.id, name=city_name_or_id)
            station.city_id = city_name_or_id
        if is_valid is not None:
            station.is_valid = is_valid
        cls._commit()

    @classmethod
    def admin_password(cls, name, password):
        return registered.admin(name, password, True)

    @classmethod
    def user_password(cls, id_card, password):
        return registered.user(None, None, id_card, password, True)

    @classmethod
    def ticket_print(cls, ticket_id):
        '''出票更新 Ticket.is_print
        '''
        ticket = get._by(Ticket, id=ticket_id, lock='read')
        ticket.is_print = True
        cls._commit()

    @classmethod
    def _commit(cls):
        session.commit()


class check:
    '''检查合法性等
    '''
    @classmethod
    def phone(cls, phone):
        return phone.isdigit() and len(phone)==11

    @classmethod
    def id_card(cls, id_card):
        assert id_card.replace('X', '').isdigit() and len(id_card)==18
        return session.execute(f"select is_id_valid('{id_card}');").first()[0]

    @classmethod
    def admin_password(cls, name, password):
        admin = get.admin(name)
        return admin.check_password(password)

    @classmethod
    def user_password(cls, id_card, password):
        user = get.user(id_card)
        return user.check_password(password)


class get:
    '''数据库数据获取
    '''
    @classmethod
    def admin(cls, name, lock=None):
        '''
        Argument:
            - name: str
            - lock: NoneType or str
        Return:
            - Admin
        '''
        return cls._by(Admin, name=name, lock=lock)

    @classmethod
    def user(cls, id_card, lock=None):
        '''
        Argument:
            - id_card: str
            - lock: NoneType or str
        Return:
            - User
        '''
        return cls._by(User, id_card_number=id_card, lock=lock)

    @classmethod
    def cities(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(session.query(City.name))

    @classmethod
    def provinces(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(session.query(City.province.distinct()))

    @classmethod
    def stations(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(cls._by(Station.name, is_valid=True, all=True))

    @classmethod
    def train_numbers(cls):
        '''
        Return:
            - list[str]
        Note:
            - 跨天：K529
        '''
        return cls._compress(cls._by(Journey.train_number.distinct(), is_valid=True, all=True))

    @classmethod
    def cities_by_province(cls, province):
        '''
        Argument:
            - province: str
        Return:
            - list[str]
        '''
        return cls._compress(cls._by(City.name, province=province, all=True))

    @classmethod
    def stations_by_city(cls, city_name):
        '''
        Argument:
            - city_name: str
        Return:
            - list[str]
        '''
        city_id = cls._by(City.id, name=city_name)
        return cls._compress(cls._by(Station.name, city_id=city_id, is_valid=True, all=True))

    @classmethod
    def orders_by_user_id(cls, user_id, iter=False):
        '''
        Argument:
            - user_id: int
            - iter: bool
        Return:
            - list[Order]
        '''
        if iter:
            return get._by(Order, user_id=user_id, iter=True)
        return get._by(Order, user_id=1, all=True)

    @classmethod
    def tickets_by_user_id(cls, user_id, iter=False):
        '''
        Argument:
            - user_id: int
            - iter: bool
        Return:
            - list[Ticket]
        '''
        if iter:
            return get._by(Ticket, user_id=user_id, iter=True)
        return get._by(Ticket, user_id=1, all=True)

    @classmethod
    def train_numbers_by_stations(cls, from_station, to_station=None):
        '''列车直达（无换乘行为）
        Argument:
            - from_station: str
            - to_station: str or None
        Return:
            - list[str]
        Note:
            - 环线：厦门、南昌、福州南、三亚、包头东、海口东
        '''
        # same stations
        if to_station is None or from_station==to_station:
            station_id = cls._by(Station.id, name=from_station, is_valid=True)
            numbers = cls._by(Journey.train_number, station_id=station_id, is_valid=True, all=True)
            counter = Counter(cls._compress(numbers))
            return [k for k, v in counter.items() if v > 1]
        # different stations
        from_station_id = cls._by(Station.id, name=from_station, is_valid=True)
        to_station_id = cls._by(Station.id, name=to_station, is_valid=True)
        if not (from_station_id is None or to_station_id):
            args = f'from_station_id={from_station_id}, to_station_id={to_station_id}'
            warn(f'Station does not exist: {args}')
            return list()
        columns = Journey.train_number, Journey.station_index
        from_train_numbers = cls._by(*columns, station_id=from_station_id, is_valid=True, all=True)
        to_train_numbers = cls._by(*columns, station_id=to_station_id, all=True)
        # find the train_number where from_station and to_station in it
        data = dict(from_train_numbers)
        return [i for i, j in to_train_numbers if (i in data and j>data[i])]

    @classmethod
    def train_numbers_by_stations_transfer(cls, from_station, to_station):
        '''列车连接（有换乘行为）
        Argument:
            - from_station: str
            - to_station: str
        Return:
            - iteration[list[train_number, Station, train_number]]
        '''
        from_station_id = cls._by(Station.id, name=from_station, is_valid=True)
        columns = Journey.train_number, Journey.station_index
        from_train_numbers = cls._by(*columns, station_id=from_station_id, is_valid=True, all=True)
        to_station_id = cls._by(Station.id, name=to_station, is_valid=True)
        to_train_numbers = cls._by(*columns, station_id=to_station_id, all=True)
        inter_columns = Journey.station_id, Journey.station_index
        # [train_number, Station, train_number]
        for number, index in from_train_numbers:
            ids = (
                i for i, j in cls._by(*inter_columns, train_number=number, is_valid=True, all=True)
                if j > index
            )
            for id in ids:
                from_second_train_numbers = cls._by(*columns, station_id=id, all=True)
                data = dict(from_second_train_numbers)
                yield from (
                    [number, get._by(Station, id=id, is_valid=True), i]
                    for i, j in to_train_numbers if (i in data and j > data[i])
                )

    @classmethod
    def journeys_by_train_number(cls, train_number, lock=None):
        '''
        Argument:
            - train_number: str
        Return:
            - list[Journey]
        '''
        return cls._by(Journey, train_number=train_number, is_valid=True, all=True, lock=lock)

    @classmethod
    def remaining_tickets_number(cls, train_number, carriage_index, depart_date):
        '''
        Argument:
            - train_number: str
            - carriage_index: int
            - depart_date: datetime.date
        '''
        total = cls._by(Capacity.seat_num, train_number=train_number, carriage_index=carriage_index, is_valid=True)
        used = cls._by(Ticket, depart_date=depart_date, count=True)
        return total[0] - used

    @classmethod
    def _compress(cls, data):
        return [d[0] for d in data]

    @classmethod
    def _by(cls, *models, all=False, count=False, iter=False, lock=None, **condition):
        try:
            query = session.query(*models).filter_by(**condition)
            if lock:
                query = query.with_lockmode(lock)
            if all:
                return query.all()
            if count:
                return query.count()
            if iter:
                return query
            return query.first()
        except:
            args = f'models={repr(models)}, all={all}, condition={condition}'
            warn(f'Query fails: {args}')
            session.rollback()
            return list() if all else None


class registered:
    '''注册或对已有用户修改密码（二次注册）
    '''
    @classmethod
    def admin(cls, name, password, chpasswd=False):
        admin = get.admin(name, lock='update')
        assert chpasswd is (admin is not None)
        if chpasswd:
            admin.set_password(password)
        else:
            admin = Admin(name=name, password=password)
            session.add(admin)
        session.commit()
        return admin

    @classmethod
    def user(cls, name, phone, id_card, password, chpasswd=False):
        if not chpasswd:
            assert check.phone(phone) and check.id_card(id_card)
        user = get.user(id_card, lock='read')
        assert chpasswd is (user is not None)
        if chpasswd:
            user.set_password(password)
        else:
            user = User(
                name=name, phone_number=phone, id_card=id_card, password=password
            )
            session.add(user)
        session.commit()
        return user


class add:
    '''处理订单，添加数据到数据库
    '''
    @classmethod
    def order(cls, user_id, train_number, carriage_index, seat_num, depart_date, depart_station, arrive_station):
        '''
        Argument:
            - user_id: int
            - train_number: str
            - carriage_index: int
            - seat_num: int
            - depart_date: datetime.date
            - depart_station: str
            - arrive_station: str
        '''
        # check whether the order is valid
        assert get._by(User, id=user_id) is not None
        # assert cache.has_train_number(train_number)  # cache train_numbers
        capacity = get._by(Capacity, train_number=train_number, carriage_index=carriage_index, is_valid=True)
        assert capacity is not None and 1<=seat_num<=capacity.seat_num  # int
        for order in get._by(Order, train_number=train_number, carriage_index=carriage_index,
                seat_num=seat_num, depart_date=depart_date, iter=True):
            assert order.status == status.canceled.value
        assert depart_date >= date.today()
        depart_station_id = get._by(Station.id, name=depart_station, is_valid=True)
        arrive_station_id = get._by(Station.id, name=arrive_station, is_valid=True)
        depart_station = get._by(Journey, train_number=train_number, station_id=depart_station_id, is_valid=True)
        arrive_station = get._by(Journey, train_number=train_number, station_id=arrive_station_id, is_valid=True)
        distance = arrive_station.distance - depart_station.distance
        assert distance > 0
        # add order
        basic_price, = get._by(SeatType.basic_price, id=capacity.seat_type)
        kwargs = {
            'status': status.booked.value, 'create_date': datetime.now(), 'user_id': user_id,
            'train_number': train_number, 'carriage_index': carriage_index, 'seat_num': seat_num,
            'depart_date': depart_date, 'depart_journey': depart_station.id,
            'arrive_journey': arrive_station.id, 'price': basic_price*distance,
        }
        order = Order(**kwargs)
        assert cls._all(order)
        return order

    @classmethod
    def ticket(cls, id=None, order=None):
        '''
        Argument:
            - id: NoneType or int
            - order: NoneType or Order
        '''
        if id is not None:
            order = get._by(Order, id=id, lock='read')
        else:
            id = order.id
        assert order is not None and order.status==status.booked.value
        order.status = status.paid.value
        ticket = Ticket(
            carriage_index=order.carriage_index, train_number=order.train_number,
            depart_date=order.depart_date, seat_num=order.seat_num, order_id=id,
            depart_journey=order.depart_journey, arrive_journey=order.arrive_journey,
        )
        assert cls._all(ticket)
        return ticket

    @classmethod
    def train(cls, train_number, seat_types, seat_nums):
        '''
        Argument:
            - train_number: str
            - seat_types: tuple[int]
            - seat_nums: tuple[int]
        '''
        for ith, (key, val) in enumerate(zip(seat_types, seat_nums)):
            assert get._by(SeatType, id=key) is not None
            carriage = Capacity(
                train_number=train_number, carriage_index=ith+1,
                seat_type=key, seat_num=val
            )
            cls._all(carriage)

    @classmethod
    def station(cls, name, city_name_or_id):
        '''
        Argument:
            - name: str
            - city_name_or_id: str or int
        '''
        station = get._by(Station, name=name)
        if isinstance(city_name_or_id, str):
            city_name_or_id, = get._by(City.id, name=city_name_or_id)
        id = get._by(Station, count=True)
        station = Station(id=id+1, name=name, city_id=city_name_or_id)
        cls._all(station)

    @classmethod
    def admin(cls, name, password):
        return registered.admin(name, password, False)

    @classmethod
    def user(cls, name, phone, id_card, password):
        return registered.user(name, phone, id_card, password, False)

    @classmethod
    def _all(cls, *instances):
        try:
            session.add_all(instances)
            session.commit()
            return True
        except Exception as e:
            print(e)
            warn(f'Add fails: instances={instances}')
            session.rollback()
            return False

    @classmethod
    def _sec_diff(cls, begin_time, end_time, day=0):
        '''
        Argument:
            - begin_time, end_time: datetime.time
            - day: int, default is 0
        Return:
            - int, seconds
        '''
        f = lambda t: 60*(60*t.hour + t.minute) + t.second
        return f(end_time) - f(begin_time) + 86400*day


class delete:
    '''删除数据库数据
    '''
    @classmethod
    def station(cls, name=None, id=None):
        '''
        Argument:
            - name: NoneType or str
            - id: NoneType or int
        '''
        if name is not None:
            station = get._by(Station, name=name, is_valid=True)
            station.is_valid = False
            id = station.id
        else:  # id is not None
            station = get._by(Station, id=id, is_valid=True)
            station.is_valid = False
        train_numbers = get._by(Journey.train_number.distinct(), station_id=id, is_valid=True, all=True)
        for train_number, in train_numbers:
            journeys = get.journeys_by_train_number(train_number, lock='read')
            for journey in journeys:
                if journey.station_id == id:
                    index = journey.station_index
                    left, right = journey.arrive_time is None, journey.depart_time is None
                    journey.station_index = - len(journeys)
                    journey.arrive_time = journey.depart_time = None
                    journey.arrive_day = journey.depart_day = None
                    journey.is_valid = False
                    break
            for journey in journeys:
                if journey.station_index > index:
                    journey.station_index -= 1
                if left and journey.station_index==index+1:
                    journey.arrive_day = journey.arrive_time = None
                if right and journey.station_index==index-1:
                    journey.depart_day = journey.depart_time = None
        cls._commit()

    @classmethod
    def train(cls, train_number):
        '''
        Argument:
            - train_number: str
        '''
        for train in get._by(Capacity, train_number=train_number, is_valid=True, iter=True):
            train.is_valid = False
        for journey in get._by(Journey, train_number=train_number, is_valid=True, iter=True):
            journey.station_index = - journey.station_index
            journey.arrive_day = journey.arrive_time = None
            journey.depart_day = journey.depart_time = None
            journey.is_valid = False
        cls._commit()

    @classmethod
    def _all(cls, *instances):
        try:
            for instance in instances:
                session.delete(instance)
            session.commit()
            return True
        except:
            warn(f'Delete fails: instances={instances}')
            session.rollback()
            return False

    @classmethod
    def _commit(cls):
        session.commit()


if __name__ == '__main__':
    if get.admin('admin') is None:
        registered.admin('admin', '12345')
    if get.user('44190019971024031X') is None:
        registered.user('user_1', '18912341234', '44190019971024031X', '1234567')
    update.admin_password('admin', '123456')
    update.user_password('44190019971024031X', '123456')

    print('Password of admin is correct')
    print(check.admin_password('admin', '123456'))

    print('Password of user_1 is correct')
    print(check.user_password('44190019971024031X', '123456'))

    print('Train numbers from 成都东 to 深圳北（没有直达的）')
    print(get.train_numbers_by_stations('成都东', '深圳北'))

    print('How many trains from 广州南 to 深圳北？')
    print(len(get.train_numbers_by_stations('广州南','深圳北')))

    print('How many trains from 深圳北 to 广州南？')
    print(len(get.train_numbers_by_stations('深圳北','广州南')))

    print('Circle line from 厦门 to 厦门')
    print(get.train_numbers_by_stations('厦门', '厦门'))

    print('Journey of D6315')
    print(get.journeys_by_train_number('D6315'))

    print('重庆北(19)到深圳北')
    print(get.train_numbers_by_stations('重庆北', '深圳北'))

    print('利川(2594)到深圳北（451）')
    print(get.train_numbers_by_stations('利川', '深圳北'))

    print('成都东 到 深圳北')
    i = get.train_numbers_by_stations_transfer('成都东', '深圳北' )
    for _ in range(10):
        print(next(i))

    print('余票信息 D1 1 号车厢')
    number = get.remaining_tickets_number('D2', 1, date(2020, 5, 20))
    print(number)

    print('订票')
    try:
        order = add.order(1, 'D1', 1, 10, date(2020, 5, 22), '北京', '沈阳南')
        ticket = add.ticket(order=order)
    except:
        ticket = get._by(Ticket)
    print(ticket)
