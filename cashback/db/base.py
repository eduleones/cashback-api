# Import all the models, so that Base has them before being
# imported by Alembic

# pylint: disable=unused-import
from cashback.db.base_class import Base  # noqa
from cashback.models.order import Order  # noqa
from cashback.models.user import User  # noqa
