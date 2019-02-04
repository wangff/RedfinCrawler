import requests
from random import randint, choice
from time import sleep
import logging

def rand_sleep():
    sleep(randint(5, 10))

class RedfinRequest:
    def __init__(self, use_proxy=False):
        self.use_proxy = use_proxy
        with open('UA.txt') as f:
            self.ua_list = [l.rstrip() for l in f.readlines()]

        if use_proxy:
            with open('proxies.txt', 'r') as f:
                self.proxy_list = [l.rstrip() for l in f.readlines()]
        else:
            self.proxy_list = []

        self.session = requests.Session()
        #  make a separate session for each proxy
        self.sessions = {}
        for proxy in self.proxy_list:
            self.sessions[proxy] = {
                'session': requests.Session(),
                'proxy': {'http': 'http://' + proxy,
                          'https': 'https://' + proxy}
            }

    def request_page_use_proxy(self, url):
        for i in range(10):
            try:
                session = self.sessions[self.random_proxy()]
                http_response = session['session'].get(url, headers=self.random_headers(),
                                                       proxies=session['proxy'], verify=False)
                if http_response.status_code == 200:
                    break
            except Exception as e:
                logging.error('request {} error.'.format(url))
            if i == 9:
                logging.critical('ip may be blocked error.')
        return http_response.text

    def request_page_no_proxy(self, url):
        for i in range(10):
            try:
                http_response = self.session.get(url, headers=self.random_headers())
                if http_response.status_code == 200:
                    logging.debug('request page {} content successfully'.format(url))
                    break
            except:
                logging.debug('make request {} failed. retry.'.format(url))

        if i == 9:
            logging.critical('make single page request {} blocked.'.format(url))

        return http_response.text

    def make_page_request(self, url: str):
        '''
        Request a URL. Before get, we sleep random seconds in case be blocked by Redfin.com
        use a loop to handle various http request errors and retry
        if 5 fails reached assume we've been blocked
        '''
        logging.info('request url {}.'.format(url))

        rand_sleep()
        if self.use_proxy:
            return self.request_page_use_proxy(url)
        else:
            return self.request_page_no_proxy(url)
        
    def random_headers(self):
        request_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
        }
        ua_count = len(self.ua_list)
        if ua_count == 0:
            # default
            request_headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) ' \
                                            'AppleWebKit/537.36 (KHTML, like Gecko)' \
                                            ' Chrome/70.0.3538.110 Safari/537.36'
        else:
            request_headers['User-Agent'] = choice(self.ua_list)

        return request_headers

    def random_proxy(self):
        proxy_count = len(self.proxy_list)
        if proxy_count == 0:
            raise RuntimeError('')
        else:
            return choice(self.proxy_list)

