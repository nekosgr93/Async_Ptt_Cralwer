import pytest
import re
import json
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Ptt_Crawlers.ptt_search import Base_Crawler


def add_test_raw_content(text, category, filename):
    path = 'tests/test_data/'
    file_name = path + 'test_{}_{}.html'.format(category, filename)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)


def add_test_result(data, category, filename):
    path = 'tests/test_data/'
    file_name = path + 'test_{}_{}.json'.format(category, filename)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def add_test_case():
    loop = asyncio.get_event_loop()
    try:
        crawler = Base_Crawler(query_str='D750',
                               title_filter=r'\[售\/.+\]',
                               add_test_data=True)
        loop.run_until_complete(crawler.parse())

        if crawler.raw_articles:
            for url, item in crawler.raw_articles.items():
                filename = url.split('/')[-1][:-5]
                add_test_raw_content(item['raw_content'], 'article', filename)
                add_test_result(item['result'], 'article', filename)
    finally:
        loop.close()


@pytest.mark.test_crawler
@pytest.mark.asyncio
async def test_crawler():
    assert os.listdir('tests/test_data'), 'Test data directory is empty! Add some test case'

    crawler = Base_Crawler(query_str='D750',
                           title_filter=r'\[售\/.+\]')

    for filename in os.listdir('tests/test_data'):
        if re.findall(r'test_article_.*\.html$', filename):
            file_id = re.findall(r'test_article_(.*)\.html$', filename)[0]
            _filename = 'tests/test_data/' + filename[:-5]
            url = 'https://www.ptt.cc/bbs/DC_SALE/' + file_id + '.html'
            with open(_filename + '.html', 'r', encoding='utf-8') as f:
                raw = f.read()
                crawl_result = crawler.extract_article_content(url, raw)
            with open(_filename + '.json', 'r', encoding='utf-8') as d:
                save_result = json.load(d)
            assert crawl_result == save_result

    await crawler.parse()
