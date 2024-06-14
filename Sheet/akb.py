# import os
# import requests
# import asyncio
# import json
# from playwright.async_api import async_playwright
# from dotenv import load_dotenv
#
# load_dotenv()
#
# MARGARIT_USERNAME = os.environ.get('MARGARIT_USER')
# MARGARIT_PASSWORD = os.environ.get('MARGARIT_PASSWORD')
#
#
# async def use_playwright():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()
#         await page.goto('https://margarittotash.salesdoc.io/site/login')
#         username = page.locator('[name="LoginForm[username]"]')
#         await username.fill(MARGARIT_USERNAME)
#         password = page.get_by_placeholder('Пароль')
#         await password.fill(MARGARIT_PASSWORD)
#         button = page.get_by_role('button')
#         await button.click()
#         await page.goto('https://margarittotash.salesdoc.io/report/saleDetail/pivotData?date_load=2024-05-17,2024-06-14')
#         informations = await page.query_selector('pre')
#         raw_data = await informations.text_content()
#         datas = json.loads(raw_data)
#         ctx = []
#         for data in datas:
#             ctx.append({
#                 'client_id': data[1],
#                 'agent_id': data[2],
#                 'product_id': data[6],
#                 'date_ordered': data[13]
#             })
#         finally_data = {}
#         for data in ctx:
#             product_id = data['product_id']
#             if product_id not in finally_data:
#                 finally_data[product_id] = []
#             finally_data[product_id].append(data)
#         return finally_data
#
#
# def prepare_params(authorize: dict, id: int, method: str, filter_argument: str):
#     userID = authorize['result']['userId']
#     token = authorize['result']['token']
#     params = {
#         'auth': {
#             'userId': userID,
#             'token': token
#         },
#         'method': method,
#         'params': {
#             'filter': {
#                 filter_argument: {
#                     'SD_id': id
#                 }
#             }
#         }
#     }
#     return params
#
#
# def authorize_user():
#     url = 'https://margarittotash.salesdoc.io/api/v2'
#     params = {
#         'method': 'login',
#         'auth': {
#             'login': MARGARIT_USERNAME,
#             'password': MARGARIT_PASSWORD
#
#         }
#     }
#     response = requests.post(url, json=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return "Error"
#
#
# def categorize_product(category_bulut_ids: list, category_margarit_ids: list):
#     datas = use_playwright()
#     authorize = authorize_user()
#     url = 'https://margarittotash.salesdoc.io/api/v2'
#     returning_data = {
#         "Bulut": [],
#         "Margarit": []
#     }
#     for product_id, data in datas.items():
#         if product_id != 'product_id':
#             params = prepare_params(authorize, product_id, 'getProduct', 'products')
#             response = requests.get(url, json=params)
#             if response.status_code == 200:
#                 product = response.json()
#                 category_id = product['result']['product'][0]['category']['CS_id']
#                 if category_id in category_bulut_ids:
#                     returning_data["Bulut"].append(data)
#                 if category_id in category_margarit_ids:
#                     returning_data["Margarit"].append(data)
#
#     return returning_data
#
#
# def grouped_clients():
#     category_bulut_ids = ['d0_1', 'd0_2', 'd0_3', 'd0_4', 'd0_5', 'd0_10']
#     category_margarit_ids = ['d0_11', 'd0_13', 'd0_15', 'd0_18', 'd0_19', 'd0_20', 'd0_6', 'd0_7', 'd0_8']
#     datas = categorize_product(category_bulut_ids, category_margarit_ids)
#     authorize = authorize_user()
#     url = 'https://margarittotash.salesdoc.io/api/v2'
#     ctx = {
#         "Bulut": [],
#         "Margarit": []
#     }
#     for key, vals in datas.items():
#         for val in vals:
#             if isinstance(val, dict):
#                 client_id = val.get('client_id', None)
#             elif isinstance(val, list) and val:
#                 client_id = val[0].get('client_id', None)
#             else:
#                 client_id = None
#             params = prepare_params(authorize, client_id, 'getClient', 'client')
#             response = requests.get(url, json=params)
#             if response.status_code == 200:
#                 client = response.json()
#                 client_name = client['result']['client'][0]['name']
#                 temp = {
#                     'client_name': client_name,
#                     'agent_id': val.get('agent_id', 'N/A') if isinstance(val, dict) else val[0].get('agent_id', 'N/A'),
#                     'date_created': val.get('date_ordered', 'N/A') if isinstance(val, dict) else val[0].get(
#                         'date_ordered', 'N/A')
#                 }
#                 if key == 'Bulut':
#                     ctx["Bulut"].append(temp)
#                 else:
#                     ctx["Margarit"].append(temp)
#
#     return ctx
#
#
# def grouped_agent_clients():
#     grouped = grouped_clients()
#     authorize = authorize_user()
#     url = 'https://margarittotash.salesdoc.io/api/v2'
#     for key, vals in grouped.items():
#         for val in vals:
#             agent_id = val['agent_id']
#             params = prepare_params(authorize, agent_id, 'getAgent', 'agent')
#             response = requests.get(url, json=params)
#             if response.status_code == 200:
#                 agent = response.json()
#                 agent_name = agent['result']['agent'][0]['name']
#                 val['agent_id'] = agent_name
#
#     return grouped

import os
import asyncio
import aiohttp
import json
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

MARGARIT_USERNAME = os.environ.get('MARGARIT_USER')
MARGARIT_PASSWORD = os.environ.get('MARGARIT_PASSWORD')


async def use_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://margarittotash.salesdoc.io/site/login')
        username = page.locator('[name="LoginForm[username]"]')
        await username.fill(MARGARIT_USERNAME)
        password = page.get_by_placeholder('Пароль')
        await password.fill(MARGARIT_PASSWORD)
        button = page.get_by_role('button')
        await button.click()
        await page.goto('https://margarittotash.salesdoc.io/report/saleDetail/pivotData?date_load=2024-05-17,2024-06-14')
        informations = await page.query_selector('pre')
        raw_data = await informations.text_content()
        datas = json.loads(raw_data)
        ctx = []
        for data in datas:
            ctx.append({
                'client_id': data[1],
                'agent_id': data[2],
                'product_id': data[6],
                'date_ordered': data[13]
            })
        finally_data = {}
        for data in ctx:
            product_id = data['product_id']
            if product_id not in finally_data:
                finally_data[product_id] = []
            finally_data[product_id].append(data)
        return finally_data


def prepare_params(authorize: dict, id: int, method: str, filter_argument: str):
    userID = authorize['result']['userId']
    token = authorize['result']['token']
    params = {
        'auth': {
            'userId': userID,
            'token': token
        },
        'method': method,
        'params': {
            'filter': {
                filter_argument: {
                    'SD_id': id
                }
            }
        }
    }
    return params


async def authorize_user():
    url = 'https://margarittotash.salesdoc.io/api/v2'
    params = {
        'method': 'login',
        'auth': {
            'login': MARGARIT_USERNAME,
            'password': MARGARIT_PASSWORD
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return "Error"


async def categorize_product(category_bulut_ids: list, category_margarit_ids: list):
    datas = await use_playwright()
    authorize = await authorize_user()
    url = 'https://margarittotash.salesdoc.io/api/v2'
    returning_data = {
        "Bulut": [],
        "Margarit": []
    }
    async with aiohttp.ClientSession() as session:
        for product_id, data in datas.items():
            if product_id != 'product_id':
                params = prepare_params(authorize, product_id, 'getProduct', 'products')
                async with session.get(url, json=params) as response:
                    if response.status == 200:
                        product = await response.json()
                        category_id = product['result']['product'][0]['category']['CS_id']
                        if category_id in category_bulut_ids:
                            returning_data["Bulut"].append(data)
                        if category_id in category_margarit_ids:
                            returning_data["Margarit"].append(data)
    return returning_data


async def grouped_clients():
    category_bulut_ids = ['d0_1', 'd0_2', 'd0_3', 'd0_4', 'd0_5', 'd0_10']
    category_margarit_ids = ['d0_11', 'd0_13', 'd0_15', 'd0_18', 'd0_19', 'd0_20', 'd0_6', 'd0_7', 'd0_8']
    datas = await categorize_product(category_bulut_ids, category_margarit_ids)
    authorize = await authorize_user()
    url = 'https://margarittotash.salesdoc.io/api/v2'
    ctx = {
        "Bulut": [],
        "Margarit": []
    }
    async with aiohttp.ClientSession() as session:
        for key, vals in datas.items():
            for val in vals:
                if isinstance(val, dict):
                    client_id = val.get('client_id', None)
                elif isinstance(val, list) and val:
                    client_id = val[0].get('client_id', None)
                else:
                    client_id = None
                params = prepare_params(authorize, client_id, 'getClient', 'client')
                async with session.get(url, json=params) as response:
                    if response.status == 200:
                        client = await response.json()
                        client_name = client['result']['client'][0]['name']
                        temp = {
                            'client_name': client_name,
                            'agent_id': val.get('agent_id', 'N/A') if isinstance(val, dict) else val[0].get('agent_id', 'N/A'),
                            'date_created': val.get('date_ordered', 'N/A') if isinstance(val, dict) else val[0].get('date_ordered', 'N/A')
                        }
                        if key == 'Bulut':
                            ctx["Bulut"].append(temp)
                        else:
                            ctx["Margarit"].append(temp)
    return ctx


async def grouped_agent_clients():
    try:
        grouped = await grouped_clients()
        authorize = await authorize_user()
        url = 'https://margarittotash.salesdoc.io/api/v2'
        async with aiohttp.ClientSession() as session:
            for key, vals in grouped.items():
                for val in vals:
                    agent_id = val['agent_id']
                    params = prepare_params(authorize, agent_id, 'getAgent', 'agent')
                    async with session.get(url, json=params) as response:
                        if response.status == 200:
                            agent = await response.json()
                            agent_name = agent['result']['agent'][0]['name']
                            val['agent_id'] = agent_name
        return grouped
    except Exception:
        return False