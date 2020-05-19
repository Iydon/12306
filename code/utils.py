from collections import Counter
from enum import Enum
from warnings import warn

from database import (
    Admin, User, City, Order, Station, Journey, SeatType, Capacity,
    session,
)


status = Enum('status', ('booked', 'paid', 'canceled'))


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
        assert admin is not None
        return admin.check_password(password)

    @classmethod
    def user_password(cls, id_card, password):
        user = get.user(id_card)
        assert user is not None
        return user.check_password(password)


class get:
    '''数据库数据获取
    '''
    @classmethod
    def admin(cls, name):
        '''
        Argument:
            - name: str

        Return:
            - Admin
        '''
        return cls._by(Admin, name=name)

    @classmethod
    def user(cls, id_card):
        '''
        Argument:
            - id_card: str

        Return:
            - User
        '''
        return cls._by(User, id_card_number=id_card)

    @classmethod
    def cities(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(session.query(City.name))

    @classmethod
    def province(cls):
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
        return cls._compress(session.query(Station.name))

    @classmethod
    def train_numbers(cls):
        '''
        Return:
            - list[str]

        Note:
            - 跨天：K529
        '''
        return cls._compress(session.query(Journey.train_number.distinct()))

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
        print(city_id)
        return cls._compress(cls._by(Station.name, city_id=city_id, all=True))

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
            station_id = cls._by(Station.id, name=from_station)
            numbers = cls._by(Journey.train_number, station_id=station_id, all=True)
            counter = Counter(cls._compress(numbers))
            return [k for k, v in counter.items() if v > 1]
        # different stations
        from_station_id = cls._by(Station.id, name=from_station)
        to_station_id = cls._by(Station.id, name=to_station)
        if not (from_station_id is None or to_station_id):
            args = f'from_station_id={from_station_id}, to_station_id={to_station_id}'
            warn(f'Station does not exist: {args}')
            return list()
        columns = Journey.train_number, Journey.station_index
        from_train_numbers = cls._by(*columns, station_id=from_station_id, all=True)
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
        from_station_id = cls._by(Station.id, name=from_station)
        columns = Journey.train_number, Journey.station_index
        from_train_numbers = cls._by(*columns, station_id=from_station_id, all=True)
        to_station_id = cls._by(Station.id, name=to_station)
        to_train_numbers = cls._by(*columns, station_id=to_station_id, all=True)
        inter_columns = Journey.station_id, Journey.station_index
        # [train_number, Station, train_number]
        for number, index in from_train_numbers:
            ids = (
                i for i, j in cls._by(*inter_columns, train_number=number, all=True)
                if j > index
            )
            for id in ids:
                from_second_train_numbers = cls._by(*columns, station_id=id, all=True)
                data = dict(from_second_train_numbers)
                yield from (
                    [number, get._by(Station, id=id), i]
                    for i, j in to_train_numbers if (i in data and j > data[i])
                )

    @classmethod
    def journeys_by_train_number(cls, train_number):
        '''
        Argument:
            - train_number: str

        Return:
            - list[Journey]
        '''
        return cls._by(Journey, train_number=train_number, all=True)

    @classmethod
    def _compress(cls, data):
        return [d[0] for d in data]

    @classmethod
    def _by(cls, *models, all=False, **condition):
        try:
            query = session.query(*models).filter_by(**condition)
            return query.all() if all else query.first()
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
        admin = get.admin(name)
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
        assert check.phone(phone) and check.id_card(id_card)
        user = get.user(id_card)
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


if __name__ == '__main__':
    if get.admin('admin_2') is None:
        registered.admin('admin_2', '12345')
    if get.admin('user_2') is None:
        registered.user('user_2', '18912341234', '44190019971024031X', '1234567')
    registered.admin('user_2', '123456', chpasswd=True)
    registered.user('user_2', '18912341234', '44190019971024031X', '123456', chpasswd=True)

    print('Password of admin_2 is correct')
    print(check.admin_password('admin_2', '123456'))

    print('Password of user_2 is correct')
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
