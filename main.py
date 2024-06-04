from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from datum import use_playwright, get_calls_fast

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
    ctx = []
    call_sales = use_playwright()
    calls = get_calls_fast()
    ctx.append({
        'chart_data': calls,
        'call_sales': call_sales
    })
    return ctx


app.include_router(router)
