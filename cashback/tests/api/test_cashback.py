import pytest
from starlette.testclient import TestClient

from cashback.main import app
from cashback.tests.conftest import user_authentication_headers
from cashback.tests.factories import create_random_user

client = TestClient(app)


class TestAPICashback:
    @pytest.mark.vcr()
    def test_get_cashback_with_superuser(
        self, payload_new_order, superuser_token_headers
    ):
        # Create user
        cpf = "345.123.434-55"
        user, _ = create_random_user(cpf=cpf)

        # Add order
        payload_new_order["cpf"] = user.cpf
        client.post(
            f"/orders/",
            headers=superuser_token_headers,
            json=payload_new_order,
        )

        # Get total cashback
        response = client.get(
            f"/cashback/{user.cpf}/", headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json() == {"cpf": "34512343455", "credit": 1586}

    @pytest.mark.vcr()
    def test_get_cashback_with_normal_user(self, payload_new_order):
        # Create user
        cpf = "343.655.878-33"
        user, user_pass = create_random_user(cpf=cpf)
        payload_new_order["cpf"] = user.cpf

        headers = user_authentication_headers(user.email, user_pass)

        # Add order
        payload_new_order["cpf"] = user.cpf
        client.post(
            f"/orders/", headers=headers, json=payload_new_order,
        )

        # Get total cashback
        response = client.get(f"/cashback/{user.cpf}/", headers=headers,)
        assert response.status_code == 200
        assert response.json() == {"cpf": "34365587833", "credit": 2825}

    def test_get_cashback_with_cpf_not_found(
        self, payload_new_order, superuser_token_headers
    ):
        response = client.get(
            f"/cashback/3434546565/", headers=superuser_token_headers,
        )
        assert response.status_code == 404

    def test_get_cashback_with_normal_user_and_divergent_cpf(
        self, payload_new_order, normal_user_token_headers
    ):
        response = client.get(
            f"/cashback/3435565776/", headers=normal_user_token_headers,
        )
        assert response.status_code == 403
