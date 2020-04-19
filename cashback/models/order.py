import datetime
import enum
import logging

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Sequence,
    String,
    event,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from cashback.core import config
from cashback.db.base_class import Base

logger = logging.getLogger(__name__)


class OrderStatus(enum.Enum):
    IN_VALIDATION = 0
    APPROVED = 1


class Order(Base):
    id = Column(
        Integer, Sequence("order_id_seq"), primary_key=True, index=True
    )
    code = Column(String(50))
    value = Column(Numeric(10, 2))
    cashback_percentage = Column(Integer)
    cashback_value = Column(Numeric(10, 2))
    status = Column(
        Enum(OrderStatus), default=OrderStatus.IN_VALIDATION, nullable=False
    )
    date = Column(DateTime)
    reseller_cpf = Column(String(20), ForeignKey("user.cpf"))
    reseller = relationship("User", back_populates="orders")
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.datetime.now())

    @hybrid_property
    def order_status(self):
        return self.status.name

    def set_order_status(self):
        "Set auto approve status if CPF number has in config"
        if self.reseller_cpf in config.CPFS_WITH_AUTO_APPROVE:
            self.status = OrderStatus.APPROVED
        return self.status

    def calculate_cashback_value(self):
        "Calcute cashback value"
        for rule in config.CASHBACK_RULES:
            if round(rule[1], 2) <= round(self.value, 2) <= round(rule[2], 2):
                self.cashback_percentage = rule[0]
                self.cashback_value = self.value * rule[0] / 100
        return self.cashback_value, self.cashback_percentage

    def set_saved_order_log(self):
        logger.info(
            f"Saved Order - reseller: {self.reseller_cpf}, code: {self.code}, "
            f"value: {self.value}, cashback_value: {self.cashback_value}"
        )


@event.listens_for(Order, "before_insert")
def order_before_insert(mapper, connect, target):
    target.set_order_status()
    target.calculate_cashback_value()


@event.listens_for(Order, "after_insert")
def order_after_insert(mapper, connect, target):
    target.set_saved_order_log()
