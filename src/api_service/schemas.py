from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date


class ParsedDataSchema(BaseModel):
    exchange_product_id: Optional[str]
    exchange_product_name: Optional[str]
    oil_id: Optional[str]
    delivery_basis_id: Optional[str]
    delivery_basis_name: Optional[str]
    delivery_type_id: Optional[str]
    volume: Optional[int]
    total: Optional[int]
    count: Optional[int]
    date: Optional[date]
    created_on: Optional[date]
    updated_on: Optional[date]

    model_config = ConfigDict(
        from_attributes=True
    )
    

# --- Эндпоинт /last_dates ---

class LastDatesResponse(BaseModel):
    dates: List[date]


# --- Эндпоинт /dynamics ---

class DynamicsRequest(BaseModel):
    oil_id: Optional[str] = None
    delivery_type_id: Optional[str] = None
    delivery_basis_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# --- Эндпоинт /results ---

class ResultsRequest(BaseModel):
    oil_id: Optional[str] = None
    delivery_type_id: Optional[str] = None
    delivery_basis_id: Optional[str] = None