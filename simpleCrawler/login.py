try:
    from urllib import urlencode
    from urllib2 import build_opener, HTTPCookieProcessor, Request
    from cookielib import CookieJar
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import build_opener, HTTPCookieProcessor, Request
    from http.cookiejar import CookieJar

import lxml.html


def parse_form(html):
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        data[e.get('name')] = e.get('value')
    return data


def main():
    login_url = 'http://example.webscraping.com/user/login'
    login_email = 'example@webscraping.com'
    login_password = 'example'
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))
    html = opener.open(login_url).read()
    form = parse_form(html)
    form['email'] = login_email
    form['password'] = login_password
    encoded_form = urlencode(form)
    request = Request(login_url, encoded_form)
    response = opener.open(request)
    print(response.geturl())


if __name__ == '__main__':
    main()
