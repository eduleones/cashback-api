# pylint: disable=trailing-whitespace
import os
from decimal import Decimal

from decouple import config

PROJECT_NAME = config("PROJECT_NAME", default="cashback", cast=str)

SECRET_KEY = config("SECRET_KEY", cast=str)

if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)


ACCESS_TOKEN_EXPIRE_MINUTES = (
    60 * 24 * 8
)  # 60 minutes * 24 hours * 8 days = 8 days


# Logging configuration, as JSON, to stdout.
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_VARS = config("LOG_VARS").replace('"', "")
JSON_LOGS = config("JSON_LOGS", default=False, cast=bool)
if JSON_LOGS:
    log_format = " ".join(
        ["%({0:s})".format(variable) for variable in LOG_VARS.split()]
    )
else:
    log_format = ""
    for index, variable in enumerate(LOG_VARS.split()):
        if variable != "message":
            if index > 0:
                log_format += ":"
            log_format += f"%({variable})s"
        else:
            log_format += f" :: %({variable})s"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": LOG_LEVEL, "handlers": ["console"]},
    "formatters": {
        "default": {"format": log_format, "datefmt": "%Y%m%d.%H%M%S"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
            "formatter": "default",
        }
    },
    "loggers": {
        # default for all undefined Python modules
        "": {"level": "WARNING", "handlers": ["console"]}
    },
}

if JSON_LOGS:
    LOGGING["formatters"]["default"][
        "class"
    ] = "pythonjsonlogger.jsonlogger.JsonFormatter"


# Database
DB_HOST = config("DB_HOST", cast=str)
DB_PORT = config("DB_PORT", default=5234, cast=int)
DB_USER = config("DB_USER", cast=str)
DB_PASSWORD = config("DB_PASSWORD", cast=str)
DB_NAME = config("DB_NAME", cast=str)

if config("TESTING", default=False, cast=bool):
    DB_NAME = "test_" + DB_NAME

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# User
FIRST_SUPERUSER_EMAIL = config("FIRST_SUPERUSER_EMAIL", cast=str)
FIRST_SUPERUSER_PASSWORD = config("FIRST_SUPERUSER_PASSWORD", cast=str)


# CPF's with auto approve status in Orders
CPFS_WITH_AUTO_APPROVE = [
    "15350946056",
]

### Cashback rules
# Configure rules to calculate cashback per Order
# (percent, start value, end value)
CASHBACK_RULES = (
    (10, Decimal("0"), Decimal("999.99")),
    (15, Decimal("1000"), Decimal("1499.99")),
    (20, Decimal("1500"), Decimal("100000000")),
)

### Extensions
# Boticario
BOTICARIO_BASE_URL = config("BOTICARIO_BASE_URL", cast=str)
BOTICARIO_API_TOKEN = config("BOTICARIO_API_TOKEN", cast=str)
