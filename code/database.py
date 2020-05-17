__all__ = ('session', 'Admin', 'User', 'City', 'Order', 'Station', 'Journey', 'SeatType', 'Capacity')


from sqlalchemy import (
    Column, Sequence, String, Integer, Float, Time, Date, TIMESTAMP,
    ForeignKey, text, create_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from werkzeug.security import generate_password_hash, check_password_hash

from config import database_url


Base = declarative_base()
engine = create_engine(database_url)
DBSession = sessionmaker(bind=engine)
session = DBSession()


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __init__(self, admin_name, password):
        self.admin_name = admin_name
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    phone_number = Column(String(11), nullable=False)
    id_card_number = Column(String(18), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __init__(self, user_name, phone_number, id_card_num, password):
        self.user_name = user_name
        self.phone_number = phone_number
        self.id_card_num = id_card_num
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    province = Column(String(30), nullable=False)


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    status = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    create_date = Column(TIMESTAMP, nullable=False, default=text('current_timestamp + interval \'8 hours\''))
    user_id = Column(Integer, ForeignKey('user.id'))


class Station(Base):
    __tablename__ = 'station'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    city_id = Column(Integer, ForeignKey('city.id'))


class Journey(Base):
    __tablename__ = 'journey'

    id = Column(Integer, primary_key=True)
    train_id = Column(String(8), nullable=False, unique=True)
    station_index = Column(Integer, nullable=False, unique=True)
    distance = Column(Integer, nullable=False)
    arrive_time = Column(Time)
    depart_time = Column(Time)
    arrive_day = Column(Integer)
    depart_day = Column(Integer)
    station_id = Column(Integer, ForeignKey('station.id'))

    def __repr__(self):
        f = lambda x: not x.startswith('_')
        g = lambda k, v: f'{k}={repr(v)}'
        items = self.__dict__.items()
        return f'Journey({", ".join(g(k, v) for k, v in items if f(k))})'


class SeatType(Base):
    __tablename__ = 'seat_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    basic_price = Column(Float, nullable=False)


class Capacity(Base):
    __tablename__ = 'capacity'

    train_number = Column(String(20), primary_key=True, nullable=False)
    carriage_index = Column(Integer, primary_key=True, nullable=False)
    seat_num = Column(Integer, nullable=False)
    seat_type = Column(Integer, ForeignKey('seat_type.id'))


class Tickets(Base):
    '''
    Question:
        - column without carriage train number: depart_journey and arrive_journey
    '''
    __tablename__ = 'ticket'

    ticket_id = Column(Integer, primary_key=True)
    carriage_id = Column(Integer, nullable=False)
    depart_date = Column(Date, nullable=False)
    seat_num = Column(String(10), nullable=False)
    order_id = Column(Integer, ForeignKey('order.id'))
    depart_journey = Column(Integer, ForeignKey('journey.id'))
    arrive_journey = Column(Integer, ForeignKey('journey.id'))


if __name__ == '__main__':
    print('Admin', session.query(Admin).count())
    print('User', session.query(User).count())
    print('City', session.query(City).count())
    print('Order', session.query(Order).count())
    print('Station', session.query(Station).count())
    print('Journey', session.query(Journey).count())
    print('SeatType', session.query(SeatType).count())
    print('Capacity', session.query(Capacity).count())
