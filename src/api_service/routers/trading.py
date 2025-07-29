from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from api_service.models import ParsedData
from api_service.schemas import LastDatesResponse, ParsedDataSchema, DynamicsRequest, ResultsRequest
from api_service.database import get_db
from api_service.redis_cache import get_redis, get_redis_ttl
import json


router = APIRouter(prefix="/trading", tags=["Trading Results"])


# Зависимость для получения Redis-клиента
async def get_redis_client():
    return await get_redis()


# Вспомогательная функция для генерации ключей кэша
def generate_cache_key(prefix: str, **kwargs) -> str:
    params = "_".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    return f"{prefix}:{params}"


@router.get("/last_dates", response_model=LastDatesResponse)
async def get_last_trading_dates(
    n: int = Query(5, ge=1),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis_client)
):
    """
    Возвращает список последних торговых дат.
    """
    cache_key = f"last_dates:{n}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # Запрос к БД
    result = await db.execute(
        select(ParsedData.date)
        .distinct()
        .order_by(ParsedData.date.desc())
        .limit(n)
    )
    rows = result.all()
    dates = [row[0].isoformat() for row in rows]

    response = {"dates": dates}
    await redis.setex(cache_key, get_redis_ttl(), json.dumps(response))
    return response


@router.get("/dynamics", response_model=List[ParsedDataSchema])
async def get_dynamics(
    request: DynamicsRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis_client)
):
    """
    Возвращает данные о торгах за определённый период с фильтрами.
    """
    cache_key = generate_cache_key("dynamics", **request.model_dump())
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # Формируем запрос
    query = select(ParsedData)

    if request.oil_id:
        query = query.where(ParsedData.oil_id == request.oil_id)
    if request.delivery_type_id:
        query = query.where(ParsedData.delivery_type_id ==
                            request.delivery_type_id)
    if request.delivery_basis_id:
        query = query.where(ParsedData.delivery_basis_id ==
                            request.delivery_basis_id)
    if request.start_date:
        query = query.where(ParsedData.date >= request.start_date)
    if request.end_date:
        query = query.where(ParsedData.date <= request.end_date)

    result = await db.execute(query)
    rows = result.all()
    data = [item.to_dict() for item, in rows]

    await redis.setex(cache_key, get_redis_ttl(), json.dumps(data))
    return data


@router.get("/results", response_model=List[ParsedDataSchema])
async def get_trading_results(
    request: ResultsRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis_client),
):
    """
    Возвращает последние торги по заданным фильтрам.
    """
    cache_key = generate_cache_key("results", **request.model_dump())
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # Получаем последнюю дату торгов
    last_date_query = (
        select(ParsedData.date)
        .distinct()
        .order_by(ParsedData.date.desc())
        .limit(1)
    )
    last_date_result = await db.execute(last_date_query)
    last_date = last_date_result.scalar_one_or_none()

    if not last_date:
        return []

    # Формируем запрос с фильтром по последней дате
    query = select(ParsedData).where(ParsedData.date == last_date)

    if request.oil_id:
        query = query.where(ParsedData.oil_id == request.oil_id)
    if request.delivery_type_id:
        query = query.where(ParsedData.delivery_type_id ==
                            request.delivery_type_id)
    if request.delivery_basis_id:
        query = query.where(ParsedData.delivery_basis_id ==
                            request.delivery_basis_id)

    result = await db.execute(query)
    rows = result.all()
    data = [item.to_dict() for item, in rows]

    await redis.setex(cache_key, get_redis_ttl(), json.dumps(data))
    return data
