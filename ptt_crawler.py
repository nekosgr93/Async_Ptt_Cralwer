# Standerd Library
import re
import time
from urllib.parse import urljoin
# Third Party
import requests
from bs4 import BeautifulSoup

# Local Module
from .ptt_logger import Ptt_Logger


class Ptt_Crawler():

    start_url = 'https://www.ptt.cc/bbs/DC_SALE/index.html'
    page = 1
    total_page = 2
    sleep_time = 2
    logger = Ptt_Logger()

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

    def parse(self):
        items = []
        for page in self.parse_nextpage():
            for article in page.select('.r-ent'):
                try:
                    if re.findall(r'\[售/[^\s]+\]', article.select_one('.title a').text):

                        meta_item, article_item = self.extract_article(article)
                    else:
                        raise AttributeError

                except AttributeError:
                    continue
                else:
                    if meta_item and article_item is not None:
                        meta_item['content'] = article_item
                        items.append(meta_item)

                    time.sleep(self.sleep_time)

        return items

    def parse_nextpage(self):
        '''Return a page soup and also parse a next Page link to get next page

        Returns:
            soup [Beautiful] -- a page which contains many articles
        '''
        next_page_url = self.start_url

        while next_page_url:
            print(next_page_url)
            try:
                resp = requests.get(next_page_url)
                resp.raise_for_status()

            except requests.exceptions.HTTPError:
                self.logger.exception('Network error! {}'.format(next_page_url))
                break

            else:
                soup = BeautifulSoup(resp.text, 'lxml')
                if self.page < self.total_page:
                    try:
                        next_page = soup.select('.btn-group.btn-group-paging .btn.wide')[1]
                    except IndexError:
                        self.logger.error('No next page section! {}'.format(next_page_url))
                        next_page_url = ''
                    else:
                        next_page_url = urljoin(self.start_url, next_page.get('href', None))
                    self.page += 1
                else:
                    next_page_url = ''

                yield soup
                time.sleep(self.sleep_time)

    def extract_article(self, meta_data):
        meta = {}
        meta['title'] = meta_data.select_one('.title a').text
        meta['author'] = meta_data.select_one('.meta .author').text
        meta['article_url'] = urljoin(self.start_url, meta_data.select_one('.title a').get('href'))

        article_item = None, None

        resp = requests.get(meta['article_url'])
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            self.logger.exception('Can\'t connect to the article! {}'.format(meta['article_url']))
        else:
            soup = BeautifulSoup(resp.text, 'lxml')
            date = soup.select('.article-metaline')[2].select_one('.article-meta-value').text
            meta['date'] = self.change_to_datetime(date)
            for x in soup.select('.article-metaline'):
                x.decompose()
            soup.select_one('.article-metaline-right').decompose()
            article_item = soup.select_one('#main-content').text.split('--')[0]

        return meta, article_item

    def extract_article_items(self, meta_data):
        """
        Parse Article Meta data to extract
            1. title
            2. author
            3. article_url
        And then use the article_url to parse the article content

        Arguments:
            meta_data {type:BeautifulSoup} -- An article meta data extract from BeautifulSoup
        """
        meta = {}
        meta['title'] = meta_data.select_one('.title a').text
        meta['author'] = meta_data.select_one('.meta .author').text
        meta['article_url'] = urljoin(self.start_url, meta_data.select_one('.title a').get('href'))

        meta_item, article_item = None, None

        resp = requests.get(meta['article_url'])
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            self.logger.exception('Can\'t connect to the article! {}'.format(meta['article_url']))
        else:
            soup = BeautifulSoup(resp.text, 'lxml')

            try:
                if re.findall('<span class="f3 hl">【物品內容】</span>', resp.text):
                    meta_item, article_item = self.parse_regular_article(soup, meta)
                else:
                    meta_item, article_item = self.parse_unregular_article(soup, meta)
                assert len(article_item) == 2

            except Exception:
                self.logger.exception('Somthing get wrong on article parsing! {}'.format(meta['article_url']))
                article_item = None
            else:
                try:
                    article_item = self.extract_multiple_items(article_item)
                except (AssertionError, KeyError):
                    self.logger.exception('Can\'t extract the article! {}'.format(meta['article_url']))
                    article_item = None

        return meta_item, article_item

    def parse_regular_article(self, soup, meta_item):
        # extract the real time and do the first data cleaning
        meta_item['date'] = soup.select('.article-metaline')[2].select_one('.article-meta-value').text

        tags = {
            '【物品內容】': 'name',
            '【交易價格】': 'price'
            }

        article_contents = soup.select('#main-content .f3.hl')
        article_item = {}
        for tag in tags:
            for content in article_contents:
                if re.findall(tag, content.text):
                    article_item[tags[tag]] = content.next_sibling.strip()

        return meta_item, article_item

    def parse_unregular_article(self, soup, meta_item):
        meta_item['date'] = self.change_to_datetime(
                                soup.select('.article-metaline')[2].select_one('.article-meta-value').text)

        tags = {
            '【物品內容】': 'name',
            '【交易價格】': 'price'
            }

        article_contents = soup.select_one('#main-content').text
        article_item = {}
        for tag in tags:
            article_item[tags[tag]] = re.findall(r'{}(.*?)【'.format(tag), article_contents, re.M | re.S)[0]

        return meta_item, article_item

    def extract_multiple_items(self, article_item):
        '''Do the second data cleaning.
        If there is more than one item in the article,
        extract them.

        Let the price just contains numbers.

        Arguments:
            article_item {[type]} -- [description]
        '''

        if re.findall(r'\n\d\.', article_item['name']):
            item_list = re.findall(r'\d\.\s*(.*)', article_item['name'])
        else:
            item_list = [article_item['name'].replace('\n', '')]

        price_list = re.findall(r'\D*(\d{3,})\D*', article_item['price'].replace(',', ''), re.S )

        assert len(item_list) == len(price_list)

        article_item['name'] = item_list
        article_item['price'] = price_list

        return article_item

    def change_to_datetime(self, datetime_string):
        date_time = re.split(r'\s+', datetime_string)[1:]

        return '{}-{}-{} {}'.format(date_time[3],
                                    self.month[date_time[0]],
                                    date_time[1],
                                    date_time[2])
