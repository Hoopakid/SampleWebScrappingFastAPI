import os
import asyncio
from time import sleep
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from datetime import datetime
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
