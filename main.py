import os
from fastapi import FastAPI, APIRouter
import logging
from fastapi.middleware.cors import CORSMiddleware

from Bitrix.formatting import format_bitrix_data
from all import get_datas
from scrapping import use_playwright, take_screenshot, convert_to_xlsx
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


@router.get('/data')
def get_data():
    leads = [{
        'Bakhriddinov Azizbek': 43,
        'Navruza ': 59,
        'Zuhra': 159,
        'Каримова Камола': 174,
        'Dilnoza': 16,
    }]
    call_sales = use_playwright()
    data = {
        "call_sales": call_sales,
        "leads": leads
    }
    # for call in call_sales:
    #     for key, val in call.items():
    #         key = [i for i in leads[0].keys() if i.lower() == key.lower()]
    #         lead = leads[0].get(key[0])
    #         data.append({
    #             key[0]: {
    #                 'sales_count': val['sales_count'],
    #                 'sales_price': val['sales_price'],
    #                 'lead': lead,
    #                 'conversion': f'{round(val["sales_count"] / lead * 100, 2)}%'
    #             }
    #         })
    return data


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
        logging.info('Started')
        datas = await get_datas()
        logging.info('Got')
        if datas == False:
            return {"status": 400, "detail": "There are some problems with Margarit, please try again later!"}
        return FileResponse('inserting_data.xlsx', filename=os.path.basename('inserting_data.xlsx'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
