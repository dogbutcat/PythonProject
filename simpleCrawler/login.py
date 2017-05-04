import urllib,urllib2
import cookielib
import lxml.html

def parse_form(html):
    tree=lxml.html.fromstring(html)
    data={}
    for e in tree.cssselect('form input'):
        data[e.get('name')]=e.get('value')
    return data

def main():
    LOGIN_URL='http://example.webscraping.com/user/login'
    LOGIN_EMAIL='example@webscraping.com'
    LOGIN_PASSWORD='example'
    cj=cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(LOGIN_URL).read()
    form = parse_form(html)
    form['email']=LOGIN_EMAIL
    form['password']=LOGIN_PASSWORD
    encoded_form = urllib.urlencode(form)
    request=urllib2.Request(LOGIN_URL,encoded_form)
    response = opener.open(request)
    print response.geturl()

if __name__ == '__main__':
    main()