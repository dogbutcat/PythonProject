from selenium import webdriver
import time
import re
import os
import csv

DEVICE_NAME = 'Apple iPhone 6'
WIDTH = 375
HEIGHT = 667
PIXEL_RATIO = 3
TARGET_URL = 'https://h5.m.taobao.com/app/movie/pages/index/index.html'
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko)' \
     ' Version/9.0 Mobile/13B143 Safari/601.1'
FIELDS = {
    'name': '.movie-name a',
    'date': '.xslide-item a',
    'film_time': '.item-clock',
    'price': '.item-price'
}


def write_csv(*arg):
    file_name = 'films.csv'
    head_row = list(FIELDS.iterkeys() if hasattr(FIELDS, 'iterkeys') else FIELDS.keys())
    with open(file_name, 'a') if os.path.exists(file_name)\
            else open(file_name, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        if 'w' in csv_file.mode:
            csv_writer.writerow(head_row)
        csv_writer.writerow(map(lambda a: a, arg))


def act_tap(web_elem, touch_action, delay=1):
    time.sleep(delay)
    touch_action.tap(web_elem)
    touch_action.perform()
    touch_action._actions.pop()


def get_films(driver, web_elems, touch_action):
    films_len = len(web_elems)
    date_pattern = re.compile('\d+-\d+')
    for i in range(films_len):
        film = web_elems[i]
        act_tap(film, touch_action)
        name = driver.find_elements_by_css_selector(FIELDS['name'])[0].text
        dates_btn = driver.find_elements_by_css_selector(FIELDS['date'])
        for j in range(len(dates_btn)):
            act_tap(dates_btn[j], touch_action)
            # date = dates_btn[j].text[3:-1] if u'\u60e0' in dates_btn[j].text else dates_btn[j].text[3:]
            date = date_pattern.findall(dates_btn[j].text)[0]
            times = filter(
                lambda elem: elem.is_displayed(),
                driver.find_elements_by_css_selector(FIELDS['film_time']))
            prices = filter(
                lambda elem: elem.is_displayed(),
                driver.find_elements_by_css_selector(FIELDS['price']))
            items_len = len(prices)
            row = []
            for k in range(items_len):
                write_csv(name, date, times[k].text, prices[k].text)
                print (name + ' ' + date + ' ' + times[k].text + ' ' + prices[k].text)
        print ('\n')


def main():
    # mobile_emulation={'deviceMetrics':{'width':WIDTH,'height':HEIGHT,'pixelRatio':PIXEL_RATIO},'userAgent':UA}
    mobile_emulation = {'deviceName': DEVICE_NAME}
    options = webdriver.ChromeOptions()
    # options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1')
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    try:
        driver = webdriver.Chrome(
            executable_path="chromedriver", chrome_options=options)
        # driver = webdriver.Remote(desired_capabilities=options.to_capabilities())
        driver.implicitly_wait(15)
        touch_action = webdriver.TouchActions(
            driver)  # Action Chain need to perform()
        driver.get(TARGET_URL)
        buyLinks = driver.find_elements_by_class_name('right-btn-red')
        act_tap(buyLinks[0], touch_action)

        cinemaLinks = driver.find_elements_by_class_name('list-item-in')
        act_tap(cinemaLinks[0], touch_action)

        cinemaFilmsLis = driver.find_elements_by_css_selector(
            '.scroll-layer li')

        get_films(driver, cinemaFilmsLis, touch_action)
    except Exception as e:
        print (e.message or e.msg)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
