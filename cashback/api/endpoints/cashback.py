import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from cashback import crud
from cashback.api.utils.db import get_db
from cashback.api.utils.security import get_current_active_user
from cashback.extensions.boticario.backends import BoticarioBackend
from cashback.models.user import User as DBUser
from cashback.schemas.cashback import Cashback

logger = logging.getLogger(__name__)
router = APIRouter()

# pylint: disable=too-many-arguments
@router.get("/cashback/{cpf}/", response_model=Cashback)
def get_total_cashback(
    *,
    db: Session = Depends(get_db),
    cpf: str,
    current_user: DBUser = Depends(get_current_active_user),
):
    """
    Total Cashback.
    """
    if (current_user.cpf != cpf) and not current_user.is_superuser:
        msg = f"The user doesn't have enough privileges"
        logger.debug(msg)
        raise HTTPException(status_code=403, detail=msg)

    user = crud.user.get_by_cpf(db, cpf=cpf)
    if not user:
        msg = f"CPF: {cpf} not found"
        logger.debug(msg)
        raise HTTPException(
            status_code=404, detail=msg,
        )

    backend = BoticarioBackend()
    credit = backend.get_total_cashback(cpf=cpf)
    body = {"cpf": cpf, "credit": credit}

    logger.info(f"Get Total Cashback with success, {cpf} - {credit}")
    return body
