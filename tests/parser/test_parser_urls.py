import pytest
from datetime import datetime
from parser_service.parser import ParserTrade

@pytest.mark.asyncio
async def test_generate_urls():
    parser = ParserTrade(max_pages=2, min_date=datetime(2023,1,1))
    urls = []
    async for url in parser.generate_urls():
        urls.append(url)
        
        
    assert len(urls) == 2
    assert "page=page-1" in urls[0]
    assert "page=page-2" in urls[1]