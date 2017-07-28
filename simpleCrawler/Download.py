import time

try:
    from urlparse import urlparse
    from urllib2 import Request, build_opener, ProxyHandler
except ImportError:
    from urllib.parse import urlparse
    from urllib.request import Request, build_opener, ProxyHandler

import random
from datetime import datetime


class Download:
    def __init__(self,
                 delay=5,
                 headers=None,
                 proxies=None,
                 num_retries=1,
                 cache=None):
        self.throttle = Throttle(delay)
        self.headers = headers
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError as e:
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    result = None
        if result is not None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = self.headers
            result = self.download(url, headers, self.num_retries, proxy=proxy)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, num_retries, data=None, proxy=None):
        """ Download Main Function """
        print('Downloading:', url)
        request = Request(url, data, headers or {})
        opener = build_opener()
        if proxy:
            proxy_params = {urlparse(url).scheme: proxy}
            opener.add_handler(ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except Exception as e:
            print('Download failed:', str(e))
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= e.code < 600:
                    return self._get(url, headers, num_retries - 1, data, proxy)
            else:
                code = None
        return {'html': html, 'code': code}


class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
