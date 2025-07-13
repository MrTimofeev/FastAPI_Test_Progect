from pydantic import BaseModel
from datetime import datetime


class ParserData(BaseModel):
    id: int
    exchange_product_id = str
    exchange_product_name = str
    oil_id = str
    delivery_basis_id = str
    delivery_basis_name = str
    delivery_type_id = str
    volume = int
    total = int
    count = int
    date = datetime
    created_on = datetime
    updated_on = datetime