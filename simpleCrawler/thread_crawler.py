import re
import time
import threading
import urlparse
import robotparser
from Download import Download
from scrap_top import scrapeTopCallback
SLEEP_TIME = 1


def thread_crawler(seed_url,
                   link_regex,
                   user_agent='wswp',
                   headers=None,
                   max_depth=-1,
                   proxies=None,
                   scrape_callback=None,
                   num_retries=1,
                   delay=10,
                   timeout=60,
                   cache=None,
                   max_threads=10):
    crawler_queue = [seed_url]
    seen = {seed_url:0}
    headers = headers or {}
    headers['User-agent'] = user_agent
    rp = get_robot(seed_url)
    D = Download(
        delay=delay,
        headers=headers,
        num_retries=num_retries,
        proxies=proxies,
        cache=cache)

    def thread_queue():
        while True:
            try:
                url = crawler_queue.pop()
                if not rp.can_fetch(user_agent,url):
                    raise KeyError('{} is blocked by {}!'.format(user_agent,url))
            except IndexError:
                break
            else:
                depth = seen[url]
                html = D(url)
                if max_depth!=depth:
                    if scrape_callback:
                        try:
                            links = scrape_callback(url, html) or []
                            if link_regex:
                                links.extend(
                                    link for link in get_links(html) 
                                    if re.match(link_regex,link))
                        except Exception as e:
                            print 'Error in callback for: {}: {}'.format(url, e)
                        else:
                            for link in links:
                                link = normalize(seed_url, link)
                                if link not in seen:
                                    seen[link]=depth+1
                                    crawler_queue.append(link)

    threads = []
    while threads or crawler_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawler_queue:
            thread = threading.Thread(target=thread_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)


def normalize(seed_url, link):
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url, link)

def same_domain(url1,url2):
    return urlparse.urlparse(url1).netloc==urlparse.urlparse(url2).netloc

def get_robot(seed_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(seed_url,'/robots.txt'))
    rp.read()
    return rp

def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=[\'"](.*?)[\'"]',re.IGNORECASE)
    return webpage_regex.findall(html)

if __name__ == '__main__':
    print 'started!'
    thread_crawler(
        'http://www.alexa.com/',
        '/topsites/?(global;\d*)?',
        user_agent='AlexaBot',
        scrape_callback=scrapeTopCallback())
