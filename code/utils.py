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
        return cls._(Admins, Admins.admin_name==name)

    @classmethod
    def user(cls, id_card):
        return cls._(Users, Users.id_card_num==id_card)

    @classmethod
    def _(cls, model, condition):
        return session.query(model).filter(condition).first()


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
