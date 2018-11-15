import pytest
import requests
from requests.exceptions import HTTPError
from ..ptt_search import Ptt_Crawler


def add_test_case(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status
    except HTTPError:
        print('HttpConnection Error')
    else:
        file_name = 'ptt' + hash(url.split('/')[-1]) + '.html'
        path = 'test_data/' + file_name
        with open(path, encoding='utf-8') as f:
            f.write(resp.text)

def test_ptt_crawler():
    crawler = Ptt_Crawler
    

