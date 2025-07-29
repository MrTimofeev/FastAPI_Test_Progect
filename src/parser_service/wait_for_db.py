import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def wait_for_db():
    engine = create_async_engine(DATABASE_URL, echo=False)
    for _ in range(15):  # Пробуем до 15 раз с интервалом 2 секунды
        try:
            async with engine.begin():
                print("База данных готова!")
                return
        except (OperationalError, Exception) as e:
            print(f"Жду базу данных... Ошибка: {e}")
            await asyncio.sleep(2)
    raise Exception("Не удалось подключиться к БД")

if __name__ == "__main__":
    asyncio.run(wait_for_db())