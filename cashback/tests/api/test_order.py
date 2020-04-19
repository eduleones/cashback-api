from starlette.testclient import TestClient

from cashback.main import app
from cashback.tests.conftest import user_authentication_headers
from cashback.tests.factories import create_random_user

client = TestClient(app)


class TestAPIOrder:
    def test_create_order_with_success(
        self, payload_new_order, normal_user_token_headers
    ):
        cpf = "123.456.678-99"
        user, _ = create_random_user(cpf=cpf)
        payload_new_order["cpf"] = user.cpf

        response = client.post(
            f"/orders/",
            headers=normal_user_token_headers,
            json=payload_new_order,
        )

        assert response.status_code == 201
        assert response.json()["order_status"] == "IN_VALIDATION"

    def test_error_create_order_without_cpf(
        self, payload_new_order, normal_user_token_headers
    ):
        payload_new_order["cpf"] = ""

        response = client.post(
            f"/orders/",
            headers=normal_user_token_headers,
            json=payload_new_order,
        )

        assert response.status_code == 409

    def test_error_create_order_without_any_field(
        self, payload_new_order, normal_user_token_headers
    ):
        payload_new_order.pop("code")

        response = client.post(
            f"/orders/",
            headers=normal_user_token_headers,
            json=payload_new_order,
        )

        assert response.status_code == 422

    def test_list_orders_with_superuser(
        self, payload_new_order, superuser_token_headers
    ):
        # Create user_1 and add order
        cpf_1 = "123.422.566-88"
        user_1, _ = create_random_user(cpf=cpf_1)
        payload_new_order["cpf"] = user_1.cpf

        client.post(
            f"/orders/",
            headers=superuser_token_headers,
            json=payload_new_order,
        )

        # Create user_2 and add order
        cpf_2 = "345.767.877-22"
        user_2, _ = create_random_user(cpf=cpf_2)
        payload_new_order["cpf"] = user_2.cpf

        client.post(
            f"/orders/",
            headers=superuser_token_headers,
            json=payload_new_order,
        )

        response = client.get(f"/orders/", headers=superuser_token_headers)
        orders = response.json()

        assert len(orders) >= 2

        reseller_cpf_list = []
        for order in orders:
            reseller_cpf_list.append(order["reseller_cpf"])

        assert "12342256688" in reseller_cpf_list
        assert "34576787722" in reseller_cpf_list

    def test_list_orders_with_superuser_and_cpf_query(
        self, payload_new_order, superuser_token_headers
    ):
        # Create user_1 and add order
        cpf_1 = "874.343.545-12"
        user_1, _ = create_random_user(cpf=cpf_1)
        payload_new_order["cpf"] = user_1.cpf

        client.post(
            f"/orders/",
            headers=superuser_token_headers,
            json=payload_new_order,
        )

        # Create user_2 and add order
        cpf_2 = "433.656.343-11"
        user_2, _ = create_random_user(cpf=cpf_2)
        payload_new_order["cpf"] = user_2.cpf

        client.post(
            f"/orders/",
            headers=superuser_token_headers,
            json=payload_new_order,
        )

        response = client.get(
            f"/orders/?cpf=43365634311", headers=superuser_token_headers,
        )
        orders = response.json()

        assert len(orders) == 1
        assert orders[0]["reseller_cpf"] == "43365634311"

    def test_error_list_orders_with_not_found_cpf(
        self, payload_new_order, superuser_token_headers
    ):
        response = client.get(
            f"/orders/?cpf=3434348398493", headers=superuser_token_headers,
        )
        assert response.status_code == 404

    def test_list_orders_with_normal_user(self, payload_new_order):
        cpf = "001.456.678-33"
        user, user_pass = create_random_user(cpf=cpf)
        payload_new_order["cpf"] = user.cpf

        headers = user_authentication_headers(user.email, user_pass)

        client.post(
            f"/orders/", headers=headers, json=payload_new_order,
        )

        response = client.get(f"/orders/", headers=headers)
        orders = response.json()

        assert len(orders) == 1
        assert orders[0]["reseller_cpf"] == "00145667833"
