import os
import logging
import requests
import aiohttp
import pandas as pd

from dotenv import load_dotenv
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from time import sleep

load_dotenv()

MARGARIT_USERNAME = os.environ.get('MARGARIT_USER')
MARGARIT_PASSWORD = os.environ.get('MARGARIT_PASSWORD')
TICKET_LOGIN = os.environ.get('TICKET_UZ_LOGIN')
TICKET_PASSWORD = os.environ.get('TICKET_UZ_PASSWORD')

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
        'https://margarittotash.salesdoc.io/report/reportBuilder/getResult?reportType=order&datestart=2024-09-10&endstart=2024-06-21&bydate=DATE_LOAD&status%5B%5D=2&status%5B%5D=3&sum=on&count=on&akb=on&field=%5B%22date%22%2C%22client%22%2C%22city%22%2C%22agent%22%2C%22product%22%2C%22productCat%22%5D',
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


async def authorize_user():
    async with async_playwright() as p:
        chromium = await p.chromium.launch(headless=True)
        page = await chromium.new_page()
        await page.goto('https://uzticket.uz/index.php?r=site/login')
        await page.fill('#LoginForm_username', TICKET_LOGIN)

        await page.fill('#LoginForm_password', TICKET_PASSWORD)

        await page.click('#login-form input[type="submit"]')
        sleep(2)
        cookies = await page.context.cookies()
        for cookie in cookies:
            if cookie['name'] == 'PHPSESSID':
                return cookie['value']
    return ''


async def convert_data_to_excel():
    url = 'https://uzticket.uz/index.php?r=ticketUzs/admin'
    cookies = {'PHPSESSID': await authorize_user(), 'from_date': '20.06.2024', 'to_date': '22.06.2024'}

    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()

                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'items'})

                if table:
                    rows = []
                    tbody = table.find('tbody')
                    tfoot = table.find('tfoot')

                    if tbody:
                        for row in tbody.find_all('tr'):
                            cells = row.find_all('td')
                            row_data = [cell.text.strip() for cell in cells]
                            rows.append(row_data)

                    tfoot_rows = []
                    if tfoot:
                        for row in tfoot.find_all('tr'):
                            cells = row.find_all('td')
                            row_data = [cell.text.strip() for cell in cells]
                            tfoot_rows.append(row_data)

                    column_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']

                    if rows:
                        df = pd.DataFrame(rows)
                        if len(df.columns) == len(column_names):
                            df.columns = column_names
                        df.to_excel('tbody.xlsx', index=False)

                    if tfoot_rows:
                        tfoot_df = pd.DataFrame(tfoot_rows)
                        if len(tfoot_df.columns) == len(column_names):
                            tfoot_df.columns = column_names
                        tfoot_df.to_excel('tfoot.xlsx', index=False)

                    # Now read and process the data
                    tbody_df = pd.read_excel('tbody.xlsx', usecols=['1', '18'])
                    tfoot_df = pd.read_excel('tfoot.xlsx', usecols=['18'])

                    data = {}
                    for idx, row in tbody_df.iterrows():
                        value1 = row['1']
                        value18 = row['18']
                        if value1 not in data:
                            data[value1] = {
                                'responsible_user': value1,
                                'opportunity': value18,
                                'count': 1
                            }
                        else:
                            data[value1]['opportunity'] += value18
                            data[value1]['count'] += 1

                    value_all = 0
                    for idx, row in tfoot_df.iterrows():
                        value_all = row['18']

                    finally_data = [value_all, ]
                    for key, val in data.items():
                        finally_data.append(val)

                    return finally_data

    return []
