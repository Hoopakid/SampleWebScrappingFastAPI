from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pprint import pprint
from datum import use_playwright

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
    data = []
    for call in call_sales:
        for key, val in call.items():
            key = [i for i in leads[0].keys() if i.lower() == key.lower()]
            lead = leads[0].get(key[0])
            data.append({
                key[0]: {
                    'sales_count': val['sales_count'],
                    'sales_price': val['sales_price'],
                    'lead': lead,
                    'conversion': f'{round(val["sales_count"] / lead * 100, 2)}%'
                }
            })
    return data


app.include_router(router)
