from fastapi import FastAPI
from routers.trading import router as trading_router

app = FastAPI(title="Spimex Trading Results API")

# Подключаем маршруты
app.include_router(trading_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Spimex Trading API"}