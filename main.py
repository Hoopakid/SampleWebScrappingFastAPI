import os
from http.client import TEMPORARY_REDIRECT

from fastapi import FastAPI, APIRouter
import logging
from fastapi.middleware.cors import CORSMiddleware

from Bitrix.formatting import format_bitrix_data
from all import getting_data, convert_data_to_excel
from scrapping import use_playwright, take_screenshot, convert_to_xlsx, translate_word
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from Sheet.akb import grouped_agent_clients

app = FastAPI()
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)


@router.get('/data-google-sheet')
async def get_google_sheet():
    try:
        bitrix_data = await format_bitrix_data()
        if bitrix_data == False:
            return {"status": 400, "detail": "There are some problems with Bitrix, please try again later!"}
        return {"status": 200, "data": bitrix_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/get-akb-data')
async def get_akb_data():
    try:
        akb_data = await grouped_agent_clients()
        if akb_data == False:
            return {"status": 400, "detail": "There are some problems with AKB, please try again later!"}
        return {"status": 200, "data": akb_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/get-all-data')
async def get_all_data():
    try:
        logging.info('Starting data retrieval')
        datas = await getting_data()
        logging.info('Data retrieval completed')
        if datas.get('success') == False:
            logging.error('Data retrieval failed')
            raise HTTPException(status_code=400,
                                detail="There are some problems with Margarit, please try again later!")
        return datas.get('data')
    except Exception as e:
        logging.error(f'Error in /get-all-data: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/get-ticket-data')
async def get_ticket_data():
    try:
        logging.info('Fetching data')
        data = await convert_data_to_excel()
        logging.info('Data fetched')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)
