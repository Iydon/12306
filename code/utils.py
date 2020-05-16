import re

from database import (
    Admins, Users, Cities, Orders, Stations, Journeys, SeatType, Carriages,
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
            - Admins
        '''
        return cls._by(Admins, admin_name=name)

    @classmethod
    def user(cls, id_card):
        '''
        Argument:
            - id_card: str

        Return:
            - Users
        '''
        return cls._by(Users, id_card_num=id_card)

    @classmethod
    def cities(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(session.query(Cities.city_name))

    @classmethod
    def province(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(session.query(Cities.province.distinct()))

    @classmethod
    def stations(cls):
        '''
        Return:
            - list[str]
        '''
        return cls._compress(session.query(Stations.station_name).all())

    @classmethod
    def cities_by_province(cls, province):
        '''
        Argument:
            - province: str

        Return:
            - list[str]
        '''
        return cls._compress(cls._by(Cities.city_name, province=province, all=True))

    @classmethod
    def stations_by_city(cls, city_name):
        '''
        Argument:
            - city_name: str

        Return:
            - list[str]
        '''
        city_id = cls._by(Cities.city_id, city_name=city_name)
        return cls._compress(cls._by(Stations.station_name, city_id=city_id, all=True))

    @classmethod
    def train_ids_by_stations(cls, from_station, to_station):
        '''
        Argument:
            - from_station: str
            - to_station: str

        Return:
            - list[str]
        '''
        from_station_id = cls._by(Stations.station_id, station_name=from_station)
        to_station_id = cls._by(Stations.station_id, station_name=to_station)
        columns = Journeys.train_id, Journeys.station_index
        from_train_ids = cls._by(*columns, station_id=from_station_id, all=True)
        to_train_ids = cls._by(*columns, station_id=to_station_id, all=True)
        # find the train_id where from_station and to_station in it
        data = dict(from_train_ids)
        return [i for i, j in to_train_ids if (i in data and j>data[i])]

    @classmethod
    def _compress(cls, data):
        return [d[0] for d in data]

    @classmethod
    def _by(cls, *models, all=False, **condition):
        query = session.query(*models).filter_by(**condition)
        return query.all() if all else query.first()


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
            admin = Admins(admin_name=name, password=password)
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
            user = Users(
                user_name=name, phone_number=phone,
                id_card_num=id_card, password=password
            )
            session.add(user)
        session.commit()
        return user


if __name__ == '__main__':
    pass
