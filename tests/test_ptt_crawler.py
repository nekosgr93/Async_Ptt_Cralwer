import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Ptt_Crawlers.ptt_search import Base_Crawler
from bs4 import BeautifulSoup
import requests


def add_test_data(url, category, filename):
    text = requests.get(url).text
    path = 'test_data/'
    file_name = path + 'test_{}_{}.html'.format(category, filename)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)

# @pytest.mark.asyncio
# async def test_crawler_parse():
#     url = 'https://www.ptt.cc/bbs/DC_SALE/M.1423921790.A.D8D.html'


def test_crawler_get_next_page():
    with open('tests/test_data/test_page_index.html', 'r', encoding='utf-8') as f:
        raw = f.read()
        soup = BeautifulSoup(raw, 'lxml')
        crawler = Base_Crawler()
        assert crawler._get_next_page_url(soup) == 'https://www.ptt.cc/bbs/DC_SALE/index4018.html'
