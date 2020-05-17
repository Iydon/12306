import re

from collections import Counter
from warnings import warn

from database import (
    Admin, User, City, Order, Station, Journey, SeatType, Capacity,
    session,
)


class check:
    '''检查合法性等
    '''
    @classmethod
    def phone(cls, phone):
        return phone.isdigit() and len(phone)==11

    @classmethod
    def id_card(cls, id_card):
        assert id_card.replace('X', '').isdigit()
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
        return cls._compress(session.query(Station.name).all())

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
            - list[str]
        '''
        raise NotImplementedError

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


if __name__ == '__main__':
    pass
