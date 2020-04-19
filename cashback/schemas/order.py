from datetime import date

from pydantic import BaseModel, Field


# Shared properties
class OrderBase(BaseModel):
    code: str
    value: float
    date: date
    reseller_cpf: str


# Properties to receive on Order creation
class OrderCreate(OrderBase):
    reseller_cpf: str = Field(..., alias="cpf")


# Properties to receive on Order update
class OrderUpdate(OrderBase):
    pass


# Properties shared by models stored in DB
class OrderInDBBase(OrderBase):
    id: int
    order_status: str

    class Config:
        orm_mode = True


# Properties to return to client
class Order(OrderInDBBase):
    cashback_percentage: int
    cashback_value: float
