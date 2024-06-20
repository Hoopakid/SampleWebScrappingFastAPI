import os
from http.client import TEMPORARY_REDIRECT

from fastapi import FastAPI, APIRouter
import logging
from fastapi.middleware.cors import CORSMiddleware

from Bitrix.formatting import format_bitrix_data
from all import get_datas
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


@router.get('/data')
async def get_data():
    try:
        call_sales = await use_playwright()
        return call_sales
    except TEMPORARY_REDIRECT as e:
        raise HTTPException(status_code=303, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/scrapped-photo')
async def get_scrapped_photo():
    try:
        file_path = await take_screenshot()
        return FileResponse(file_path, filename=os.path.basename(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/get-excel-data')
async def get_excel_data():
    try:
        excel = await convert_to_xlsx()
        if excel == True:
            return FileResponse('data.xlsx', filename=os.path.basename('data.xlsx'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        datas = await get_datas()
        logging.info('Data retrieval completed')
        if datas == False:
            logging.error('Data retrieval failed')
            raise HTTPException(status_code=400,
                                detail="There are some problems with Margarit, please try again later!")
        return FileResponse('inserting_data.xlsx', filename=os.path.basename('inserting_data.xlsx'))
    except Exception as e:
        logging.error(f'Error in /get-all-data: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/translate-word')
async def translate_words(word: str, lang1: str, lang2: str):
    try:
        logging.info('Translating word')
        translate = await translate_word(word, lang1, lang2)
        logging.info('Word translated')
        return {
            "success": True,
            "status": True,
            "translated_word": translate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
