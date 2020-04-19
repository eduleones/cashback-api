import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from cashback import crud
from cashback.api.utils.db import get_db
from cashback.api.utils.security import get_current_active_user
from cashback.models.user import User as DBUser
from cashback.schemas.order import Order, OrderCreate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/orders/", response_model=Order, status_code=201)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: DBUser = Depends(get_current_active_user),
):
    """
    Create new order.
    """
    cpf_user = crud.user.get_by_cpf(db, cpf=order_in.reseller_cpf)
    if not cpf_user:
        msg = (
            f"The user with this cpf {cpf_user} already exists in the system."
        )
        raise HTTPException(
            status_code=409, detail=msg,
        )

    order = crud.order.create_with_reseller(db_session=db, obj_in=order_in)
    logger.info(f"Create order with success! Order: {order.id}")
    return order


# pylint: disable=too-many-arguments
@router.get("/orders/", response_model=List[Order])
def list_orders(
    db: Session = Depends(get_db),
    cpf: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: DBUser = Depends(get_current_active_user),
):
    """
    List orders.
    """
    if current_user.is_superuser:
        if cpf:
            user = crud.user.get_by_cpf(db, cpf=cpf)
            if not user:
                logger.debug(f"Not found in list_orders - cpf: {cpf}")
                raise HTTPException(
                    status_code=404,
                    detail="The user with this cpf does not exist.",
                )

            orders = crud.order.get_multi_by_reseller(db, cpf=cpf)
        else:
            orders = crud.order.get_multi(db, skip=skip, limit=limit)
    else:
        orders = crud.order.get_multi_by_reseller(db, cpf=current_user.cpf)

    logger.info(f"Get orders with success!")
    return orders
