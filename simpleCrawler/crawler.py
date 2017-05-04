#%%
import urllib2
import urlparse
import robotparser
from datetime import datetime
import time
import re
# from ScrapeCallback import ScrapeCallback
from scrap_top import scrapeTopCallback
from Download import Download
from mongocache import MongoCache


def link_crawler(seed_url,
                 link_regex=None,
                 headers=None,
                 proxy=None,
                 user_agent='wswp',
                 delay=5,
                 max_depth=-1,
                 max_urls=-1,
                 scrawl_callback=None,
                 cache=None):
    """
        Crawler Main Function
    """
    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    rp = get_robot(seed_url)
    headers = headers or {}
    num_urls = 0
    if user_agent:
        headers['User-agent'] = user_agent
    D = Download(headers=headers, proxies=proxy, cache=cache)
    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            links = []
            depth = seen[url]
            html = D(url)
            if scrawl_callback:
                links.extend(scrawl_callback(url, html) or [])
            if depth != max_depth:
                if link_regex:
                    links.extend(
                        link for link in get_links(html)
                        if re.match(link_regex, link))
                for link in links:
                    link = normalize(seed_url, link)
                    if link not in seen:
                        seen[link] = depth + 1
                        if same_domain(seed_url, link):
                            crawl_queue.append(link)
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt', url


def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


def get_robot(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def normalize(seed_url, link):
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


if __name__ == '__main__':
    print 'started!'
    link_crawler(
        'http://www.alexa.com/',
        '/topsites',
        user_agent='AlexaBot',
        max_depth=2,
        scrawl_callback=scrapeTopCallback(),
        cache=MongoCache())

# print link_crawler('http://example.webscraping.com/','/index')
