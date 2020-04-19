import logging

import requests
from fastapi import HTTPException

from cashback.core import config

logger = logging.getLogger(__name__)


class BoticarioBackend:
    base_url = config.BOTICARIO_BASE_URL
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "token": config.BOTICARIO_API_TOKEN,
    }

    def _request_cashback(self, cpf=None):
        url = self.base_url + f"/v1/cashback?cpf={cpf}"

        try:
            response = requests.get(url, headers=self.headers)
            if (response.status_code != 200) or (
                response.json()["statusCode"] != 200
            ):
                msg = (
                    f"Error {response.status_code} in Get "
                    "total cashback in Boticario API"
                )
                logger.error(msg)
                raise HTTPException(
                    status_code=500, detail=msg,
                )

            return response.json()

        except requests.Timeout:
            msg = "Timeout error in Get total cash in Boticario API"
            logger.error(msg)
            raise HTTPException(
                status_code=500, detail=msg,
            )

    def get_total_cashback(self, cpf=None):
        response = self._request_cashback(cpf=cpf)
        return response.get("body").get("credit")
