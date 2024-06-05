import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from scrapping import use_playwright, take_screenshot
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

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


app.include_router(router)
