import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from cashback.extensions.boticario.backends import BoticarioBackend
from cashback.main import app

client = TestClient(app)


class TestExtensionsBackends:
    def setup(self):
        self.backend = BoticarioBackend()

    @pytest.mark.vcr()
    def test_get_total_cashback(self):
        cpf = "12345667899"

        total_cashback = self.backend.get_total_cashback(cpf=cpf)
        assert total_cashback == 1578

    @pytest.mark.vcr()
    def test_error_get_total_cashback_with_invalid_cpf(self):
        cpf = "123.456.678-99"

        with pytest.raises(HTTPException):
            self.backend.get_total_cashback(cpf=cpf)
