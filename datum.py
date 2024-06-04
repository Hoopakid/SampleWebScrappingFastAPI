import os
from time import sleep
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get('USER_USERNAME')
PASSWORD = os.environ.get('PASSWORD')


def use_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://panel.strawberryhouse.uz/login')
        username = page.locator('[placeholder="Логин"]')
        username.fill('DUSTYOR')

        password = page.locator('[placeholder="Пароль"]')
        password.fill('Dk77Dk11')

        page.get_by_role('button').click()
        today = datetime.now().date()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        sleep(3)
        last_day_url = f'https://panel.strawberryhouse.uz/statistics/operators?start={str(yesterday)}+00%3A00&end={str(today)}+00%3A00'
        page.goto(last_day_url)

        page.wait_for_selector('table')
        rows = page.query_selector_all('table tbody tr')
        datas = []
        for row in rows:
            data = [td.text_content() for td in row.query_selector_all('td')]
            if data[-1].endswith('сум'):
                temp = {
                    data[1]: {
                        'sales_count': int(data[6].replace(' шт', '')),
                        'sales_price': int(data[7].replace(' сум', '').replace(' ', ''))
                    }}
                datas.append(temp)
        browser.close()
    return datas


def get_calls_fast():
    datas = [
        {'Abduvohidov Sardorbek': {'all': 20, 'success': 14, 'no_success': 6}},
        {'Salihanova Umida': {'all': 11, 'success': 5, 'no_success': 6}},
        {'Dilnoza': {'all': 20, 'success': 11, 'no_success': 9}},
        {'Bakhriddinov Azizbek': {'all': 10, 'success': 6, 'no_success': 4}},
        {'ZUHRA': {'all': 15, 'success': 9, 'no_success': 6}},
        {'Мустафо': {'all': 7, 'success': 4, 'no_success': 3}},
        {'Muxammadaziz': {'all': 6, 'success': 3, 'no_success': 3}},
        {'Юсупова Нилуфар': {'all': 19, 'success': 11, 'no_success': 8}},
        {'Navruza ': {'all': 21, 'success': 10, 'no_success': 11}},
        {'Karimova Madina': {'all': 10, 'success': 3, 'no_success': 7}},
        {'Рихсибоев Рухилло': {'all': 5, 'success': 2, 'no_success': 3}}
    ]
    return datas
