from bs4 import BeautifulSoup
from datetime import datetime
import xlrd
import io
import asyncio
import aiohttp
from parser_service.models import ParsedData
from parser_service.database import engine, AsyncSessionLocal
from sqlalchemy import insert


class ParserTrade:

    def __init__(self, max_pages=100, min_date=datetime(2023, 1, 1), concurrency=3):
        self.max_pages = max_pages
        self.min_date = min_date
        self.base_url = "https://spimex.com"
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    async def generate_urls(self):
        """Генерирует список URL для парсинга"""
        for page in range(1, self.max_pages + 1):
            yield (f"{self.base_url}/markets/oil_products/trades/results/"
                   f"?page=page-{page}&bxajaxid=d609bce6ada86eff0b6f7e49e6bae904")

    async def create_tasks(self, session):
        """Создает задачи для всех страниц"""
        tasks = []
        async for url in self.generate_urls():
            tasks.append(asyncio.create_task(self._fetch_page(session, url)))
        return tasks

    async def _fetch_page(self, session, url):
        """Парсит страницу и обрабатывает найденные ссылки"""
        async with self.semaphore:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        await self._process_links(content)
                    else:
                        print(f"Ошибка при загрузке страницы {url}, статус: {response.status}")
            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")

    async def _process_links(self, response):
        """Обрабатывает ссылки, скачивает XLS, парсит и сохраняет в БД"""
        soup = BeautifulSoup(response, "lxml")
        links = soup.find_all('div', attrs={'class': 'accordeon-inner__item'})

        for link in links:
            a_tag = link.find("a", class_='accordeon-inner__item-title link xls')
            if not a_tag:
                continue

            url = self.base_url + a_tag.get('href', '').strip()
            date_span = link.find("span")

            if not date_span:
                continue

            try:
                date_parsed = datetime.strptime(date_span.text.strip(), '%d.%m.%Y')
            except ValueError:
                print(f"Неверный формат даты: {date_span.text}")
                continue

            if date_parsed < self.min_date:
                print("Дата слишком старая. Прекращаем обработку.")
                break

            if "oil_xls" in url:
                print(f"Обнаружена ссылка: {url}")
                xls_data = await self.download_xls(url)
                if xls_data:
                    await self.process_xls_and_save(xls_data, date_parsed)

    async def download_xls(self, url):
        """Скачивает файл по ссылке"""
        connector = aiohttp.TCPConnector(limit_per_host=3, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.read()
                        return io.BytesIO(content)
                    else:
                        print(f"Ошибка при загрузке файла {url}, статус: {response.status}")
                        return None
            except Exception as e:
                print(f"Ошибка при загрузке: {url}: {e}")
                return None

    async def process_xls_and_save(self, xls_data, date):
        """Обрабатывает скачанный XLS и сохраняет данные в БД"""
        try:
            book = xlrd.open_workbook(file_contents=xls_data.getvalue())
            sheet = book.sheet_by_index(0)

            data_list = []

            for row_num in range(sheet.nrows):
                cols = sheet.row_values(row_num)

                if len(cols) < 6:
                    continue

                product_id = cols[1]
                count = cols[-1]

                if len(product_id) == 11 and count.isdigit():
                    data_list.append({
                        "exchange_product_id": product_id,
                        "exchange_product_name": cols[2],
                        "oil_id": product_id[:4],
                        "delivery_basis_id": product_id[4:7],
                        "delivery_basis_name": cols[3],
                        "delivery_type_id": product_id[-1],
                        "volume": int(cols[4]),
                        "total": int(cols[5]) if '.' not in cols[5] else int(cols[5].split('.')[0]),
                        "count": int(cols[-1]),
                        "date": date.date() if hasattr(date, 'date') else date,
                    })

            if data_list:
                async with AsyncSessionLocal() as session:
                    stmt = insert(ParsedData).values(data_list)
                    await session.execute(stmt)
                    await session.commit()
                    print(f"Сохранено {len(data_list)} записей")

        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")

    async def request_site(self):
        """Запускает парсинг страниц"""
        connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = await self.create_tasks(session)
            await asyncio.gather(*tasks)

    async def _init_db(self):
        """Создаёт таблицы в БД"""
        async with engine.begin() as conn:
            await conn.run_sync(ParsedData.metadata.create_all)
        print("Таблицы созданы и проверены")

    async def run(self):
        """Основной метод запуска парсера"""
        await self._init_db()

        await self.request_site()
        print("Парсинг завершён, все данные сохранены в БД.")


if __name__ == "__main__":
    from datetime import datetime
    start = datetime.now()
    # TODO: Убрать максимальное количество страниц, чтобы по умолчанию было 100
    parser = ParserTrade(max_pages=2, min_date=datetime(2023, 1, 1))
    asyncio.run(parser.run())
    end = datetime.now()
    print(f"Затраченное время: {end - start}")