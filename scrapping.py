import os
import asyncio
import pandas as pd

from time import sleep
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get('USER_USERNAME')
PASSWORD = os.environ.get('PASSWORD')


def use_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://panel.strawberryhouse.uz/login')
        username = page.locator('[placeholder="Логин"]')
        username.fill(USERNAME)

        password = page.locator('[placeholder="Пароль"]')
        password.fill(PASSWORD)

        page.get_by_role('button').click()
        today = datetime.now().date()
        sleep(3)
        last_day_url = f'https://panel.strawberryhouse.uz/statistics/operators?start={str(today)}+00%3A00&end={str(today)}+20%3A30'
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


async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        await asyncio.sleep(2)
        await page.goto('https://test-analytic.vercel.app/')
        await asyncio.sleep(5)
        await page.screenshot(path='calls.png')
        await browser.close()
    return 'calls.png'


async def sales_by_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://panel.strawberryhouse.uz/login')
        username = page.locator('[placeholder="Логин"]')
        await username.fill('DUSTYOR')

        password = page.locator('[placeholder="Пароль"]')
        await password.fill('Dk77Dk11')

        await page.get_by_role('button').click()
        today = datetime.now().date()
        yesterday = (datetime.now() - timedelta(days=366)).date()
        sleep(3)
        last_day_url = f'https://panel.strawberryhouse.uz/statistics/clients?start={str(yesterday)}+00%3A00&end={str(yesterday)}+19%3A00'
        await page.goto(last_day_url)

        await page.wait_for_selector('table')
        rows = await page.query_selector_all('table tbody tr')
        datas = {}
        links = []
        for r in rows:
            query_selector = await r.query_selector_all('td')
            a_selector = await r.query_selector_all('a')
            data = [await td.text_content() for td in query_selector]
            if len(a_selector) != 0:
                link = await a_selector[0].get_attribute('href')
                user_link = f'https://panel.strawberryhouse.uz{link}'
                links.append({
                    data[1]: user_link
                })
                if data[-1].endswith('сум'):
                    temp = {
                        'count': int(data[2].replace(' шт', '')),
                        'price': int(data[3].replace(' сум', '').replace(' ', '')),
                    }
                    datas[data[1]] = temp

        for link in links:
            for key, val in link.items():
                await page.goto(val)
                await page.wait_for_selector('table')
                rows = await page.query_selector_all('table tbody tr')
                user_number = ''
                for r in rows:
                    query_selector = await r.query_selector_all('td')
                    for td in query_selector:
                        td_ = await td.text_content()
                        if td_.startswith('998'):
                            user_number = f'+{td_}'
                            if key in datas:
                                datas[key]['user_number'] = user_number
        await browser.close()
    return datas


async def convert_to_xlsx():
    datas = await sales_by_playwright()
    data_list = []
    for key, val in datas.items():
        data_list.append({
            'Ism': key,
            'Soni': val['count'],
            'Narxi': val['price'],
            'Telefon raqami': val.get('user_number', '')
        })

    df = pd.DataFrame(data_list, columns=['Ism', 'Soni', 'Narxi', 'Telefon raqami'])
    df.to_excel('data.xlsx', index=False)

    return True
