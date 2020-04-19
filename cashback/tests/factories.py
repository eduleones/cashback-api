import random
import string

from cashback import crud
from cashback.core import config
from cashback.db.session import db_session
from cashback.schemas.user import UserAdminCreate, UserCreate


def random_lower_string():
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email():
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_cpf():
    cpf = [random.randint(0, 9) for x in range(9)]
    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
        cpf.append(11 - val if val > 1 else 0)
    return "%s%s%s.%s%s%s.%s%s%s-%s%s" % tuple(cpf)


def create_random_user(cpf=None):
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    if not cpf:
        cpf = random_cpf()

    user = crud.user.get_by_email(db_session, email=email)
    if not user:
        user_in = UserCreate(
            email=email, password=password, full_name=full_name, cpf=cpf
        )
        user = crud.user.create(db_session=db_session, obj_in=user_in)
    return user, password


def create_superuser():
    email = config.FIRST_SUPERUSER_EMAIL
    password = config.FIRST_SUPERUSER_PASSWORD

    user = crud.user.get_by_email(db_session, email=email)
    if not user:
        user_in = UserAdminCreate(
            email=email, password=password, is_superuser=True
        )
        user = crud.user.create(db_session=db_session, obj_in=user_in)
    return user
