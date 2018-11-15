import re
import random
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import aiohttp
from time import time


class Base_Crawler():
    items = []
    page = 1
    page_soup = []
    month = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }

    def __init__(self, loop, total_page=1, numbers_of_article='all',
                 get_random_articles=False, query_str=None, title_filter=None):
        self.total_page = total_page
        self.numbers_of_article = numbers_of_article
        self.query_str = query_str
        self.title_filter = title_filter

        if self.query_str is not None:
            self.start_url = 'https://www.ptt.cc/bbs/DC_SALE/search?q={}'.format(query_str)
        else:
            self.start_url = 'https://www.ptt.cc/bbs/DC_SALE/index.html'

        self.session = aiohttp.ClientSession(loop=loop)

    @property
    def total_page(self):
        return self._total_page

    @total_page.setter
    def total_page(self, value):
        if not isinstance(value, int):
            raise Exception("[total_page] must be an integer.")
        self._total_page = value

    @property
    def numbers_of_article(self):
        return self._numbers_of_article

    @numbers_of_article.setter
    def numbers_of_article(self, value):
        if value != 'all' and not isinstance(value, int):
            raise Exception("[numbers_of_article] must be an integer. If you want to get all articles, you can set it to 'all'")
        self._numbers_of_article = value

    @property
    def get_random_articles(self):
        return self._get_random_articles

    @get_random_articles.setter
    def get_random_articles(self, value):
        if isinstance(value, bool):
            if self.numbers_of_article == 'all':
                self._get_random_articles = False
            else:
                self._get_random_articles = value
        else:
            raise Exception("[get_random_articles] must set to either True or False")

    async def main(self):
        try:
            await self._parse()
        finally:
            await self.session.close()

    async def fetch(self, url):
        async with self.session.get(url) as resp:
            assert resp.status == 200
            return await resp.text()

    async def _parse(self):
        html = await self.fetch(self.start_url)
        current_page = BeautifulSoup(html, 'lxml')

        while current_page:
            articles = self._get_articles(current_page)
            if articles:
                for article in articles:
                    try:
                        item = await self._parse_article(article)
                    except Exception as e:
                        # TODO: find exception
                        print(article.select_one('.title a').get('href', ''))
                        print(e)
                        continue
                    else:
                        self.items.append(item)

                if self.page < self.total_page:
                    try:
                        current_page = await self._get_next_page(current_page)
                    except AssertionError:
                        current_page = ''
                    self.page += 1
                else:
                    current_page = ''
            else:
                print('There\'s no articles. Try another query strings or board')
                break

    async def _get_next_page(self, current_page_soup):
        '''
        receive a current page soup and return the nextpage soup
        '''
        next_page_url = current_page_soup.select('.btn-group.btn-group-paging .btn.wide')[1].get('href', '')
        if next_page_url:
            url = urljoin(self.start_url, next_page_url)
            html = await self.fetch(url)
            next_page_soup = BeautifulSoup(html, 'lxml')
        else:
            next_page_soup = ''
        return next_page_soup

    def _get_articles(self, current_page):
        articles = current_page.select('.r-ent')
        if articles:
            if self.title_filter is not None:
                articles = [article for article in articles if self._title_fliter(article)]

            if self.numbers_of_article != 'all':
                if self.get_random_articles:
                    articles = random.sample(articles, k=self.numbers_of_article)
                else:
                    articles = articles[0:self.numbers_of_article]

        return articles

    def _title_fliter(self, article):
        title_match = False
        try:
            if re.findall(self.title_filter, article.select_one('.title a').text):
                title_match = True
        except AttributeError:
            pass
        return title_match

    async def _parse_article(self, article):
        article_url = urljoin(self.start_url, article.select_one('.title a').get('href'))
        raw_content = await self.fetch(article_url)
        item = self.extract_article_content(article_url, raw_content)
        return item

    def extract_article_content(self, url, raw_content):
        soup = BeautifulSoup(raw_content, 'lxml')
        item = {}
        meta = soup.select('.article-metaline')
        item['title'] = meta[0].extract().text
        item['author'] = meta[1].extract().text
        date = meta[2].extract().select_one('.article-meta-value').text
        item['date'] = self._change_to_datetime(date)
        item['article_url'] = url
        soup.select_one('.article-metaline-right').decompose()

        item['content'] = soup.select_one('#main-content').text.split('--')[0]
        return item

    def _change_to_datetime(self, datetime_string):
        date_time = re.split(r'\s+', datetime_string)[1:]

        return '{}-{}-{} {}'.format(date_time[3],
                                    self.month[date_time[0]],
                                    date_time[1],
                                    date_time[2])


if __name__ == '__main__':
    start = time()
    loop = asyncio.get_event_loop()
    crawler = Base_Crawler(loop=loop, query_str='D750', title_filter=r'\[售/[^\s]+\]')
    loop.run_until_complete(crawler.main())
    loop.close()
    end = time()
    print(crawler.items)
    print('Cost {} seconds'.format((end - start) / 5))
