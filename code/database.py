__all__ = ('session', 'Admins', 'Users', 'Cities', 'Orders', 'Stations', 'Journeys', 'SeatType', 'Carriages')


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


class Admins(Base):
    __tablename__ = 'admins'

    admin_id = Column(Integer, primary_key=True)
    admin_name = Column(String(30), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __init__(self, admin_name, password):
        self.admin_name = name
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(30), nullable=False)
    phone_number = Column(String(11), nullable=False)
    id_card_num = Column(String(18), nullable=False, unique=True)
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


class Cities(Base):
    __tablename__ = 'cities'

    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(30), nullable=False)
    province = Column(String(30), nullable=False)


class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_status = Column(Integer, nullable=False)
    order_price = Column(Float, nullable=False)
    create_date = Column(TIMESTAMP, nullable=False, default=text('current_timestamp + interval \'8 hours\''))
    person = Column(Integer, ForeignKey('users.user_id'))


class Stations(Base):
    __tablename__ = 'stations'

    station_id = Column(Integer, primary_key=True)
    station_name = Column(String(30), nullable=False, unique=True)
    city_id = Column(Integer, ForeignKey('cities.city_id'))


class Journeys(Base):
    __tablename__ = 'journeys'

    journey_id = Column(Integer, primary_key=True)
    train_id = Column(String(8), nullable=False, unique=True)
    station_index = Column(Integer, nullable=False, unique=True)
    distance = Column(Integer, nullable=False)
    arrive_time = Column(Time)
    depart_time = Column(Time)
    arrive_day = Column(Integer)
    depart_day = Column(Integer)
    station_id = Column(Integer, ForeignKey('stations.station_id'))


class SeatType(Base):
    __tablename__ = 'seat_type'

    seat_type_id = Column(Integer, primary_key=True)
    seat_name = Column(String(20), nullable=False, unique=True)
    seat_basic_price = Column(Float, nullable=False)


class Carriages(Base):
    __tablename__ = 'carriages'

    train_number = Column(String(8), primary_key=True, nullable=False)
    carriage_index = Column(Integer, primary_key=True, nullable=False)
    seat_num = Column(Integer, nullable=False)
    seat_type_id = Column(Integer, ForeignKey('seat_type.seat_type_id'))


class Tickets(Base):
    '''
    Question:
        - column without carriage train number: depart_journey and arrive_journey
    '''
    __tablename__ = 'tickets'

    ticket_id = Column(Integer, primary_key=True)
    carriage_id = Column(Integer, nullable=False)
    depart_date = Column(Date, nullable=False)
    seat_num = Column(String(10), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    depart_journey = Column(Integer, ForeignKey('journeys.journey_id'))
    arrive_journey = Column(Integer, ForeignKey('journeys.journey_id'))


if __name__ == '__main__':
    print('Admins', session.query(Admins).count())
    print('Users', session.query(Users).count())
    print('Cities', session.query(Cities).count())
    print('Orders', session.query(Orders).count())
    print('Stations', session.query(Stations).count())
    print('Journeys', session.query(Journeys).count())
    print('SeatType', session.query(SeatType).count())
    print('Carriage', session.query(Carriages).count())
