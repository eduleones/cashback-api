from starlette.testclient import TestClient

from cashback.core import config
from cashback.main import app

client = TestClient(app)


class TestLogin:
    def test_get_access_token(self):
        login_data = {
            "username": config.FIRST_SUPERUSER_EMAIL,
            "password": config.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"/login/access-token/", data=login_data)
        result = r.json()
        assert r.status_code == 200
        assert "access_token" in result

    def test_use_access_token(self, superuser_token_headers):
        r = client.post(f"/login/test-token/", headers=superuser_token_headers)
        assert r.status_code == 200
