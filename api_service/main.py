from fastapi import FastAPI

app = FastAPI()


@app.get("/last_dates")
def get_last_trading_dates():
    pass

@app.get("/dynamics")
def get_dynamics():
    pass

@app.get("/results")
def get_trading_results():
    pass
