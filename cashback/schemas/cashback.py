from pydantic import BaseModel


class Cashback(BaseModel):
    cpf: str
    credit: int = None
