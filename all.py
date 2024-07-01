import asyncio
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
        await username.fill(MARGARIT_USERNAME)
        password = page.get_by_placeholder('Пароль')
        await password.fill(MARGARIT_PASSWORD)
        button = page.get_by_role('button')
        await button.click()
        sleep(7)
        cookies = await context.cookies()
        cookie = get_cookie(cookies)
        if cookie == 'None':
            return {'success': False}
    yesterday = (datetime.now() - timedelta(days=1)).date()
    response = requests.get(
        f'https://margarittotash.salesdoc.io/report/reportBuilder/getResult?reportType=order&datestart={yesterday}&endstart={yesterday}&bydate=DATE&status%5B%5D=2&status%5B%5D=3&sum=on&volume=on&akb=on&field=%5B%22date%22%2C%22client%22%2C%22city%22%2C%22agent%22%2C%22product%22%2C%22productCat%22%5D',
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


async def fetch_data_for_date(session, url, cookies, date):
    cookies['from_date'] = date.strftime('%d.%m.%Y')
    cookies['to_date'] = date.strftime('%d.%m.%Y')
    async with session.get(url, cookies=cookies) as response:
        if response.status == 200:
            html = await response.text()
            return html
    return None


async def convert_data_to_excel():
    url = 'https://uzticket.uz/index.php?r=ticketUzs/admin'
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    cookies = {'PHPSESSID': await authorize_user()}

    async with aiohttp.ClientSession() as session:
        all_data = []
        for single_date in (start_of_week + timedelta(n) for n in range((today - start_of_week).days + 1)):
            html = await fetch_data_for_date(session, url, cookies, single_date)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'items'})

                if table:
                    tbody = table.find('tbody')
                    tfoot = table.find('tfoot')

                    if tbody:
                        for row in tbody.find_all('tr'):
                            cells = row.find_all('td')
                            row_data = [cell.text.strip() for cell in cells]
                            row_data.append(single_date.strftime('%A'))
                            all_data.append(row_data)

                    if tfoot:
                        tfoot_row = tfoot.find('tr')
                        cells = tfoot_row.find_all('td')
                        tfoot_data = [cell.text.strip() for cell in cells]
                        all_data.append(tfoot_data)

    if not all_data:
        return [0]

    column_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                    '19', '20', '21', 'day']
    df = pd.DataFrame(all_data)

    if len(df.columns) == len(column_names):
        df.columns = column_names

    if not df.empty:
        tbody_df = df[df['day'] != '']
        tfoot_df = df[df['day'] == '']

        data = {}
        for idx, row in tbody_df.iterrows():
            user = row['1']
            day = row['day']
            try:
                opportunity = float(row.get('18', 0) or 0)
            except (ValueError, TypeError):
                opportunity = 0
            if user not in data:
                data[user] = {
                    'name': user,
                    'today_opportunity': 0,
                    'today_count': 0,
                    'monday': 0,
                    'tuesday': 0,
                    'wednesday': 0,
                    'thursday': 0,
                    'friday': 0,
                    'saturday': 0,
                    'sunday': 0
                }
            if day:
                data[user][day.lower()] += opportunity
                if day.lower() == today.strftime('%A').lower():
                    data[user]['today_opportunity'] += opportunity
                    data[user]['today_count'] += 1

        total_sales = 0
        for idx, row in tfoot_df.iterrows():
            try:
                total_sales = float(row.get('18', 0) or 0)
            except (ValueError, TypeError):
                total_sales = 0

        finally_data = [total_sales]
        for key, val in data.items():
            finally_data.append(val)

        filtered_data = [data for data in finally_data if
                         data and data.get('name') != 'Нет результатов.' and data.get('name') != 0 and data.get(
                             'name') != '']

        return filtered_data

    return [0]
