from fastapi import FastAPI

from datum import use_playwright, get_calls_fast

app = FastAPI()


@app.get('/data')
def get_data():
    ctx = []
    call_sales = use_playwright()
    calls = get_calls_fast()
    ctx.append({
        'chart_data': calls,
        'call_sales': call_sales
    })
    return ctx
