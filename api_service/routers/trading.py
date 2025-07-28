from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models import ParsedData
from schemas import LastDatesResponse, ParsedDataSchema, DynamicsRequest, ResultsRequest
from database import get_db
from redis_cache import get_redis, get_redis_ttl
import json


router = APIRouter(prefix="/trading", tags=["Trading Results"])


# Вспомогательная функция для генерации ключей кэша
def generate_cache_key(prefix: str, **kwargs) -> str:
    params = "_".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    return f"{prefix}:{params}"


@router.get("/last_dates", response_model=LastDatesResponse)
async def get_last_trading_dates(n: int = Query(5, ge=1), db: AsyncSession = Depends(get_db)):
    """
    Возвращает список последних торговых дат.

    ## Параметры:
    - **n** (int): количество возвращаемых дат (минимум 1)

    ## Ответ:
    JSON-массив с датами в формате `YYYY-MM-DD`
    """
    cache_key = f"last_dates:{n}"
    redis = await get_redis()
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
    dates = [row[0].isoformat() for row in result.all()]

    response = {"dates": dates}

    # Сохраняем в Redis
    await redis.setex(cache_key, get_redis_ttl(), json.dumps(response))
    return response


@router.get("/dynamics", response_model=List[ParsedDataSchema])
async def get_dynamics(
    request: DynamicsRequest = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает данные о торгах за определённый период с фильтрами.

    ## Фильтры:
    - **oil_id**: идентификатор нефти
    - **delivery_type_id**: тип поставки
    - **delivery_basis_id**: базис поставки
    - **start_date**: начало периода
    - **end_date**: конец периода

    ## Ответ:
    Список записей с полной информацией о торгах
    """
    cache_key = generate_cache_key("dynamics", **request.dict())
    redis = await get_redis()
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
    data = [item.to_dict() for item, in result]

    await redis.setex(cache_key, get_redis_ttl(), json.dumps(data))
    return data


@router.get("/results", response_model=List[ParsedDataSchema])
async def get_trading_results(
    request: ResultsRequest = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает последние торги по заданным фильтрам.

    ## Фильтры:
    - **oil_id**: идентификатор нефти
    - **delivery_type_id**: тип поставки
    - **delivery_basis_id**: базис поставки

    ## Ответ:
    Список записей за самую последнюю дату торгов
    """
    
    cache_key = generate_cache_key("results", **request.dict())
    redis = await get_redis()
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
    data = [item.to_dict() for item, in result.all()]

    await redis.setex(cache_key, get_redis_ttl(), json.dumps(data))
    return data
