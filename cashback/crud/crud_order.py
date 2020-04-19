import logging
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from cashback.crud.base import CRUDBase
from cashback.crud.utils import normalize_cpf
from cashback.models.order import Order
from cashback.schemas.order import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create_with_reseller(
        self, db_session: Session, *, obj_in: OrderCreate
    ) -> Order:
        db_obj = Order(
            code=obj_in.code,
            value=Decimal(obj_in.value),
            date=obj_in.date,
            reseller_cpf=normalize_cpf(obj_in.reseller_cpf),
        )
        try:
            db_session.add(db_obj)
            db_session.commit()
            db_session.refresh(db_obj)
            return db_obj
        except Exception as err:
            logger.error(
                f"DB Rollback in CRUDOrder create_with_reseller: {err}"
            )
            db_session.rollback()
            raise

    def get_multi_by_reseller(
        self, db_session: Session, *, cpf: int, skip=0, limit=100
    ) -> List[Order]:
        return (
            db_session.query(self.model)
            .filter(Order.reseller_cpf == cpf)
            .offset(skip)
            .limit(limit)
            .all()
        )


order = CRUDOrder(Order)
