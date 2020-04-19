import pytest
from starlette.testclient import TestClient

from cashback.main import app
from cashback.tests.conftest import user_authentication_headers
from cashback.tests.factories import create_random_user

client = TestClient(app)


class TestIntegration:
    @pytest.mark.integration
    def test_api_get_cashback_with_superuser(
        self, payload_new_order, superuser_token_headers
    ):
        # Create user
        cpf = "341.343.000-12"
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
        assert response.json()["credit"] >= 0

    @pytest.mark.integration
    def test_api_get_cashback_with_normal_user(self, payload_new_order):
        # Create user
        cpf = "235.656.123-44"
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
        assert response.json()["credit"] >= 0
