from starlette.testclient import TestClient

from cashback import crud
from cashback.db.session import db_session
from cashback.main import app

client = TestClient(app)


class TestAPIUser:
    def test_list_users(self, user_in, superuser_token_headers):
        user = crud.user.create(db_session, obj_in=user_in)

        r = client.get(f"/users/", headers=superuser_token_headers)
        all_users = r.json()

        assert len(all_users) >= 1
        for user in all_users:
            assert "email" in user

    def test_error_list_users_with_normal_user(
        self, normal_user_token_headers
    ):

        r = client.get(f"/users/", headers=normal_user_token_headers)
        assert r.status_code == 403

    def test_create_new_user(
        self, payload_normal_user, superuser_token_headers
    ):
        r = client.post(
            f"/users/",
            headers=superuser_token_headers,
            data=payload_normal_user,
        )
        assert r.status_code == 201

    def test_error_in_create_user_with_existing_email(
        self, user_in, superuser_token_headers
    ):
        user = crud.user.create(db_session, obj_in=user_in)

        data = {
            "email": user.email,
            "password": "xpto123",
            "full_name": "Renato Russo",
            "cpf": "123.234.456-87",
        }

        r = client.post(
            f"/users/", headers=superuser_token_headers, json=data,
        )
        assert r.status_code == 409

    def test_error_in_create_user_with_existing_cpf(
        self, user_in, superuser_token_headers
    ):
        user = crud.user.create(db_session, obj_in=user_in)

        data = {
            "email": "renato@russo.com",
            "password": "xpto123",
            "full_name": "Renato Russo",
            "cpf": user.cpf,
        }

        r = client.post(
            f"/users/", headers=superuser_token_headers, json=data,
        )
        assert r.status_code == 409

    def test_error_in_create_user_with_normal_user(
        self, payload_normal_user, normal_user_token_headers
    ):
        r = client.post(
            f"/users/",
            headers=normal_user_token_headers,
            json=payload_normal_user,
        )
        assert r.status_code == 403

    def test_get_user_by_id(self, user_in, superuser_token_headers):
        user = crud.user.create(db_session, obj_in=user_in)

        r = client.get(f"/user/{user.id}/", headers=superuser_token_headers)
        api_user = r.json()

        assert r.status_code == 200
        assert user.email == api_user["email"]

    def test_error_get_user_by_id_with_normal_user(
        self, user_in, normal_user_token_headers
    ):
        user = crud.user.create(db_session, obj_in=user_in)
        r = client.get(f"/user/{user.id}/", headers=normal_user_token_headers)

        assert r.status_code == 403

    def test_error_get_user_by_id_not_found(
        self, user_in, superuser_token_headers
    ):
        r = client.get(f"/user/6545/", headers=superuser_token_headers)

        assert r.status_code == 404

    def test_get_current_normal_user(self, normal_user_token_headers):
        r = client.get(f"/user/profile/", headers=normal_user_token_headers)
        api_user = r.json()

        assert r.status_code == 200
        assert api_user["is_active"]

    def test_get_current_supuser(self, superuser_token_headers):
        r = client.get(f"/user/profile/", headers=superuser_token_headers)
        api_user = r.json()

        assert r.status_code == 200
        assert api_user["is_superuser"]

    def test_update_current_normal_user(self, normal_user_token_headers):
        data = {
            "full_name": "Gilberto Gil",
            "password": "xpto123",
        }

        r = client.put(
            f"/user/profile/", headers=normal_user_token_headers, json=data,
        )
        assert r.status_code == 200

        response = client.get(
            f"/user/profile/", headers=normal_user_token_headers
        )
        api_user = response.json()
        assert api_user["full_name"] == "Gilberto Gil"

    def test_update_current_normal_user_inactived(
        self, normal_user_token_headers
    ):
        data = {
            "full_name": "Chico Buarque",
            "password": "xpto123",
            "is_active": False,
        }

        r = client.put(
            f"/user/profile/", headers=normal_user_token_headers, json=data,
        )
        assert r.status_code == 200

        response = client.get(
            f"/user/profile/", headers=normal_user_token_headers
        )
        assert response.status_code == 401

    def test_update_user_by_id(
        self, normal_user_token_headers, superuser_token_headers
    ):
        r = client.get(f"/user/profile/", headers=normal_user_token_headers)
        api_user = r.json()

        data = {
            "full_name": "Caetano Veloso",
            "password": "xpto123",
            "is_active": False,
        }

        r = client.put(
            f"/user/{api_user['id']}/",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 200

        response = client.get(
            f"/user/{api_user['id']}/", headers=superuser_token_headers
        )
        api_user = response.json()
        assert api_user["full_name"] == "Caetano Veloso"
