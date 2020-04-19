from cashback import crud
from cashback.db.session import db_session
from cashback.schemas.user import UserCreate
from cashback.tests.factories import (
    random_cpf,
    random_email,
    random_lower_string,
)


class TestCrudUser:
    def test_create_user(self):
        email = random_email()
        password = random_lower_string()
        full_name = random_lower_string()
        cpf = random_cpf()

        user_in = UserCreate(
            email=email, password=password, full_name=full_name, cpf=cpf
        )
        user = crud.user.create(db_session, obj_in=user_in)
        assert user.email == email
        assert hasattr(user, "hashed_password")

    def test_authenticate_user(self):
        email = random_email()
        password = random_lower_string()
        full_name = random_lower_string()
        cpf = random_cpf()

        user_in = UserCreate(
            email=email, password=password, full_name=full_name, cpf=cpf
        )
        user = crud.user.create(db_session, obj_in=user_in)
        authenticated_user = crud.user.authenticate(
            db_session, email=email, password=password
        )
        assert authenticated_user
        assert user.id == authenticated_user.id

    def test_not_authenticate_user(self):
        email = random_email()
        password = random_lower_string()
        user = crud.user.authenticate(
            db_session, email=email, password=password
        )
        assert user is None

    def test_check_if_user_is_active(self, user_in):
        user = crud.user.create(db_session, obj_in=user_in)
        assert user.is_active

    def test_check_if_user_is_inactive(self):
        email = random_email()
        password = random_lower_string()
        full_name = random_lower_string()
        cpf = random_cpf()

        user_in = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            cpf=cpf,
            is_active=False,
        )
        user = crud.user.create(db_session, obj_in=user_in)
        assert not user.is_active

    def test_check_if_user_is_superuser(self):
        email = random_email()
        password = random_lower_string()
        full_name = random_lower_string()
        cpf = random_cpf()

        user_in = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            cpf=cpf,
            is_superuser=True,
        )
        user = crud.user.create(db_session, obj_in=user_in)
        assert user.is_superuser

    def test_check_if_user_is_normal_user(self, user_in):
        user = crud.user.create(db_session, obj_in=user_in)
        assert not user.is_superuser

    def test_get_user(self):
        email = random_email()
        password = random_lower_string()
        full_name = random_lower_string()
        cpf = random_cpf()

        user_in = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            cpf=cpf,
            is_superuser=True,
        )
        user = crud.user.create(db_session, obj_in=user_in)
        user_2 = crud.user.get(db_session, id=user.id)
        assert user.id == user_2.id

    def test_get_user_by_email(self, user_in):
        user = crud.user.create(db_session, obj_in=user_in)
        user_2 = crud.user.get_by_email(db_session, email=user.email)
        assert user.id == user_2.id

    def test_get_user_by_cpf(self, user_in):
        user = crud.user.create(db_session, obj_in=user_in)
        user_2 = crud.user.get_by_cpf(db_session, cpf=user.cpf)
        assert user.id == user_2.id
