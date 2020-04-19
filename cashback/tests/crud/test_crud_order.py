import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import DataError, IntegrityError

from cashback import crud
from cashback.core import config
from cashback.crud.utils import normalize_cpf
from cashback.db.session import db_session
from cashback.schemas.order import OrderCreate
from cashback.tests.factories import (
    create_random_user,
    random_cpf,
    random_lower_string,
)


class TestCrudOrder:
    def test_create_order_with_reseller(self, normal_user):
        code = random_lower_string()
        date = datetime.date.today()
        value = 203.99

        order_in = OrderCreate(
            code=code, date=date, value=value, cpf=normal_user.cpf
        )
        order = crud.order.create_with_reseller(db_session, obj_in=order_in)
        assert order.reseller.cpf == normalize_cpf(normal_user.cpf)

    def test_error_create_order_without_reseller(self):
        code = random_lower_string()
        date = datetime.date.today()
        value = 343.11
        cpf = random_cpf()

        order_in = OrderCreate(code=code, date=date, value=value, cpf=cpf)
        with pytest.raises(IntegrityError):
            crud.order.create_with_reseller(db_session, obj_in=order_in)

    def test_create_multi_orders_with_reseller(self, normal_user):
        code_1 = random_lower_string()
        date_1 = datetime.date.today()
        value_1 = 542.54
        cpf = normal_user.cpf

        code_2 = random_lower_string()
        date_2 = datetime.date.today()
        value_2 = 1044

        order_in_1 = OrderCreate(
            code=code_1, date=date_1, value=value_1, cpf=cpf,
        )
        order_in_2 = OrderCreate(
            code=code_2, date=date_2, value=value_2, cpf=cpf,
        )

        order_1 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_1
        )
        order_2 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_2
        )

        assert order_1.reseller.cpf == order_2.reseller.cpf

    def test_create_order_and_validate_status_with_in_validation(
        self, normal_user
    ):
        code = random_lower_string()
        date = datetime.date.today()
        value = 254.65

        order_in = OrderCreate(
            code=code, date=date, value=value, cpf=normal_user.cpf
        )
        order = crud.order.create_with_reseller(db_session, obj_in=order_in)

        assert order.status.name == "IN_VALIDATION"

    def test_create_order_and_validate_status_with_approved(self):
        code = random_lower_string()
        date = datetime.date.today()
        value = 254.65
        cpf = config.CPFS_WITH_AUTO_APPROVE[0]

        user, _ = create_random_user(cpf=cpf)

        order_in = OrderCreate(code=code, date=date, value=value, cpf=cpf)
        order = crud.order.create_with_reseller(db_session, obj_in=order_in)

        assert user.cpf == order.reseller_cpf
        assert order.status.name == "APPROVED"

    def test_calculate_cashbach_value_with_10_percent(self, normal_user):
        code = random_lower_string()
        date = datetime.date.today()
        value_1 = 577.65
        value_2 = 999.98

        order_in_1 = OrderCreate(
            code=code, date=date, value=value_1, cpf=normal_user.cpf
        )
        order_in_2 = OrderCreate(
            code=code, date=date, value=value_2, cpf=normal_user.cpf
        )
        order_1 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_1
        )
        order_2 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_2
        )

        assert order_1.cashback_value == Decimal("57.76")
        assert order_2.cashback_value == Decimal("100.00")
        assert order_1.cashback_percentage == 10
        assert order_2.cashback_percentage == 10

    def test_calculate_cashbach_value_with_15_percent(self, normal_user):
        code = random_lower_string()
        date = datetime.date.today()
        value_1 = 1250
        value_2 = 1499.99

        order_in_1 = OrderCreate(
            code=code, date=date, value=value_1, cpf=normal_user.cpf
        )
        order_in_2 = OrderCreate(
            code=code, date=date, value=value_2, cpf=normal_user.cpf
        )
        order_1 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_1
        )
        order_2 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_2
        )

        assert order_1.cashback_value == Decimal("187.50")
        assert order_2.cashback_value == Decimal("225.00")
        assert order_1.cashback_percentage == 15
        assert order_2.cashback_percentage == 15

    def test_calculate_cashbach_value_with_20_percent(self, normal_user):
        code = random_lower_string()
        date = datetime.date.today()
        value_1 = 1501.20
        value_2 = 3482

        order_in_1 = OrderCreate(
            code=code, date=date, value=value_1, cpf=normal_user.cpf
        )
        order_in_2 = OrderCreate(
            code=code, date=date, value=value_2, cpf=normal_user.cpf
        )
        order_1 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_1
        )
        order_2 = crud.order.create_with_reseller(
            db_session, obj_in=order_in_2
        )

        assert order_1.cashback_value == Decimal("300.24")
        assert order_2.cashback_value == Decimal("696.40")
        assert order_1.cashback_percentage == 20
        assert order_2.cashback_percentage == 20

    def test_error_in_calculate_cashbach_value(self, normal_user):
        code = random_lower_string()
        date = datetime.date.today()
        value = 5345379857943875984798375

        order_in = OrderCreate(
            code=code, date=date, value=value, cpf=normal_user.cpf
        )

        with pytest.raises(DataError):
            crud.order.create_with_reseller(db_session, obj_in=order_in)
