from fastapi import APIRouter

from cashback.api.endpoints.cashback import router as cashback_route
from cashback.api.endpoints.login import router as login_router
from cashback.api.endpoints.orders import router as order_route
from cashback.api.endpoints.users import router as user_router

router = APIRouter()
router.include_router(login_router, tags=["login"])
router.include_router(user_router, tags=["user"])
router.include_router(order_route, tags=["order"])
router.include_router(cashback_route, tags=["cashback"])
