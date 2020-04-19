import json

import pytest

from cashback.tests.factories import (
    random_cpf,
    random_email,
    random_lower_string,
)


@pytest.fixture
def payload_admin_user():
    return json.dumps(
        {
            "full_name": random_lower_string(),
            "email": random_email(),
            "password": random_lower_string(),
        }
    )


@pytest.fixture
def payload_normal_user():
    return json.dumps(
        {
            "full_name": random_lower_string(),
            "email": random_email(),
            "password": random_lower_string(),
            "cpf": random_cpf(),
        }
    )
