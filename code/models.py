from sqlalchemy import (
    Column, Sequence, String, Integer, Float, Time, Date, TIMESTAMP,
    ForeignKey, text, create_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Admins(Base):
    __tablename__ = 'admins'

    admin_id = Column(Integer, Sequence('admin_id_seq'), primary_key=True)
    admin_name = Column(String(30), nullable=False, unique=True)
    password = Column(String(20), nullable=False)


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_name = Column(String(30), nullable=False)
    phone_number = Column(String(11), nullable=False)
    ID_card_num = Column(String(18), nullable=False, unique=True)
    password = Column(String(16), nullable=False)


class Cities(Base):
    __tablename__ = 'cities'

    city_id = Column(Integer, Sequence('city_id_seq'), primary_key=True)
    city_name = Column(String(30), nullable=False)
    province = Column(String(30), nullable=False)


class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, Sequence('order_id_seq'), primary_key=True)
    order_status = Column(Integer, nullable=False)
    order_price = Column(Float, nullable=False)
    create_date = Column(TIMESTAMP, nullable=False, default=text('current_timestamp + interval \'8 hours\''))
    person = Column(Integer, ForeignKey('users.user_id'))


class Stations(Base):
    __tablename__ = 'stations'

    station_id = Column(Integer, Sequence('station_id_seq'), primary_key=True)
    station_name = Column(String(30), nullable=False, unique=True)
    city_id = Column(Integer, ForeignKey('cities.city_id'))


class Journeys(Base):
    __tablename__ = 'journeys'

    journey_id = Column(Integer, Sequence('journey_id_seq'), primary_key=True)
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

    seat_type_id = Column(Integer, Sequence('seat_type_id_seq'), primary_key=True)
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

    ticket_id = Column(Integer, Sequence('ticket_id_seq'), primary_key=True)
    carriage_id = Column(Integer, nullable=False)
    depart_date = Column(Date, nullable=False)
    seat_num = Column(String(10), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    depart_journey = Column(Integer, ForeignKey('journeys.journey_id'))
    arrive_journey = Column(Integer, ForeignKey('journeys.journey_id'))


if __name__ == "__main__":
    # 初始化数据库连接
    username = 'checker'
    password = '123456'
    hostport = '127.0.0.1:5432'
    database = 'project_2'
    engine = create_engine(f'postgresql://{username}:{password}@{hostport}/{database}')
    # 创建DBSession类型
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
