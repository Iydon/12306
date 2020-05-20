from datetime import date
from faker import Faker
from random import choice, randint

try:
    from .database import (
        Admin, User, City, Order, Station, Journey, SeatType, Capacity, Ticket,
        session,
    )
    from .utils import add
except:
    from database import (
        Admin, User, City, Order, Station, Journey, SeatType, Capacity, Ticket,
        session,
    )
    from utils import get, add, check, update, cache, delete


F = Faker('zh')


def add_random_user():
    try:
        add.user(
            name=F.name(), phone=F.phone_number(),
            id_card=F.ssn(), password=F.password(),
        )
        return True
    except Exception as e:
        print(e)
        return False


def add_random_admin():
    try:
        add.admin(
            name=F.name(), password=F.password(),
        )
        return True
    except Exception as e:
        print(e)
        return False


def get_random_user_id():
    user_ids = get._compress(get._by(User.id, all=True))
    return choice(user_ids)


def get_random_train_number():
    return choice(cache.train_numbers)


def get_random_index_and_number(train_number):
    index = choice(get._compress(get._by(Capacity.carriage_index, train_number=train_number, all=True)))
    total, = get._by(Capacity.seat_num, train_number=train_number, carriage_index=index)
    return index, randint(1, total)


def add_random_order_and_ticket():
    user_id = get_random_user_id()
    train_number = get_random_train_number()
    carriage_index, seat_number = get_random_index_and_number(train_number)
    depart_date = F.date_time_between_dates(date.today(), date(9999, 12, 31)).date()
    journeys = get.journeys_by_train_number(train_number)
    order = add.order(
        user_id, train_number, carriage_index, seat_number, depart_date,
        get._by(Station, id=journeys[0].station_id).name,
        get._by(Station, id=journeys[-1].station_id).name,
    )
    ticket = add.ticket(order=order)
    return order, ticket


if __name__ == '__main__':
    pass
