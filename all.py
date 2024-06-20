import os
import requests
import logging
import pandas as pd

from time import sleep
from dotenv import load_dotenv
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

load_dotenv()

MARGARIT_USERNAME = os.environ.get('MARGARIT_USER')
MARGARIT_PASSWORD = os.environ.get('MARGARIT_PASSWORD')

logging.basicConfig(level=logging.INFO)


def get_cookie(cookies):
    for cookie in cookies:
        if cookie['name'] == 'PHPSESSID':
            return cookie['value']
    return 'None'


async def getting_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://margarittotash.salesdoc.io/site/login')
        username = page.locator('[name="LoginForm[username]"]')
        await username.fill('yahyo')
        password = page.get_by_placeholder('Пароль')
        await password.fill('7777')
        button = page.get_by_role('button')
        await button.click()
        sleep(7)
        cookies = await context.cookies()
        cookie = get_cookie(cookies)
        if cookie == 'None':
            return {'success': False}
    yesterday = (datetime.now() - timedelta(days=1)).date()
    today = (datetime.now()).date()
    response = requests.get(
        'https://margarittotash.salesdoc.io/report/reportBuilder/getResult?reportType=order&datestart=2024-06-10&endstart=2024-06-21&bydate=DATE_LOAD&status%5B%5D=2&status%5B%5D=3&sum=on&count=on&akb=on&field=%5B%22date%22%2C%22client%22%2C%22city%22%2C%22agent%22%2C%22product%22%2C%22productCat%22%5D',
        cookies={'PHPSESSID': cookie})
    df = pd.DataFrame(response.json())
    df.to_csv('data.csv', index=False)
    data = pd.read_csv('data.csv')
    data = data.to_dict(orient='records')
    new_data = []
    combined = {}
    three_combined = {}
    cnt = 0

    for d in data:
        if cnt == 3:
            three_combined = dict(reversed(list(three_combined.items())))
            new_data.append({**combined, **three_combined})
            combined = {}
            three_combined = {}
            cnt = 0
        d = eval(d['data'])
        for key, value in d.items():
            if key == 'Итоги':
                three_combined[d['Итоги']] = d['value']
                break
            elif key not in combined:
                combined[key] = value
        cnt += 1
    return {'success': True, 'data': new_data}
