import os
import json
import logging

import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

MARGARIT_USERNAME = os.environ.get('MARGARIT_USER')
MARGARIT_PASSWORD = os.environ.get('MARGARIT_PASSWORD')

logging.basicConfig(level=logging.INFO)


async def get_datas():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            logging.info('Navigating to login page')
            await page.goto('https://margarittotash.salesdoc.io/site/login')

            logging.info('Filling login form')
            username = page.locator('[name="LoginForm[username]"]')
            await username.fill(MARGARIT_USERNAME)
            password = page.get_by_placeholder('Пароль')
            await password.fill(MARGARIT_PASSWORD)
            button = page.get_by_role('button')
            await button.click()

            logging.info('Navigating to report page')
            await page.goto(
                'https://margarittotash.salesdoc.io/report/reportBuilder/getResult?reportType=order&datestart=2024-06-01&endstart=2024-06-08&bydate=DATE_LOAD&status%5B%5D=2&status%5B%5D=3&sum=on&count=on&akb=on&field=%5B%22date%22%2C%22client%22%2C%22city%22%2C%22agent%22%2C%22product%22%2C%22productCat%22%5D')

            logging.info('Extracting report data')
            data = await page.query_selector('pre')
            if not data:
                raise Exception('Report data element not found')

            logging.info('Getting text content')
            raw_data = await data.text_content()
            if not raw_data:
                raise Exception('No text content found in report data element')

            logging.info('Loading data')
            raw_data = json.loads(raw_data)

            logging.info('Processing data')
            df = pd.DataFrame(raw_data)
            df.to_csv('all.csv', index=False)
            data = pd.read_csv('all.csv')
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

            logging.info('Saving processed data to Excel')
            data = pd.DataFrame(new_data)
            data.to_excel('inserting_data.xlsx', index=False)
            await browser.close()
            return True
    except Exception as e:
        logging.error(f'Error in get_datas: {e}')
        return False
