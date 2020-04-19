import logging

import pytest
from decouple import config
from sqlalchemy import create_engine
from starlette.testclient import TestClient

from cashback.core import config as settings
from cashback.db.base import Base
from cashback.main import app
from cashback.schemas.user import UserCreate
from cashback.tests.factories import (
    create_random_user,
    create_superuser,
    random_cpf,
    random_email,
    random_lower_string,
)

logger = logging.getLogger(__name__)


# pylint: disable=line-too-long
ADMIN_DSN = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f'{settings.DB_HOST}:{settings.DB_PORT}/{config("DB_NAME")}'
)

admin_engine = create_engine(ADMIN_DSN, isolation_level="AUTOCOMMIT")

TEST_DSN = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

test_engine = create_engine(TEST_DSN, isolation_level="AUTOCOMMIT")

client = TestClient(app)

# Hook commandline
def pytest_addoption(parser):
    parser.addoption(
        "--ci",
        action="store_true",
        default=False,
        help="Indicates tests are running on CI",
    )


# pylint: disable=redefined-outer-name
def setup_db(request):
    """
    Removing the old test database environment and creating new clean
    environment.
    """
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    option = request.config.getoption("--ci")

    teardown_db(request)

    if not option:
        with admin_engine.connect() as conn:
            conn.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Create database {db_name}")

            conn.execute(
                f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}"
            )

    Base.metadata.create_all(test_engine)
    logger.info(f"Create Test tables")


def teardown_db(request):
    """
    Removing the test database environment.
    """
    db_name = settings.DB_NAME
    option = request.config.getoption("--ci")

    if not option:
        with admin_engine.connect() as conn:
            conn.execute(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid();
                """
            )
            conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
            logger.info(f"DROP DATABASE {db_name}")


@pytest.yield_fixture(scope="session", autouse=True)
def db(request):
    """
    Fixture to run and tear down the database.
    """
    setup_db(request)
    yield
    teardown_db(request)


def user_authentication_headers(email, password):
    data = {"username": email, "password": password}
    response = client.post(f"/login/access-token/", data=data)
    auth_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


@pytest.fixture(scope="module", autouse=True)
def superuser_token_headers():
    user = create_superuser()
    headers = user_authentication_headers(
        user.email, settings.FIRST_SUPERUSER_PASSWORD
    )
    return headers


@pytest.fixture
def normal_user_token_headers():
    user, password = create_random_user()
    headers = user_authentication_headers(user.email, password)
    return headers


@pytest.fixture
def user_in():
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    cpf = random_cpf()

    return UserCreate(
        email=email, password=password, full_name=full_name, cpf=cpf
    )


@pytest.fixture
def normal_user():
    user, _ = create_random_user()
    return user


@pytest.fixture
def payload_new_order():
    return {
        "code": random_lower_string(),
        "value": "100",
        "date": "2020-04-18",
        "cpf": random_cpf(),
    }
