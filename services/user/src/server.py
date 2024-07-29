from fastapi import FastAPI
from api import endpoints

app = FastAPI()

app.include_router(endpoints.router)


@app.get("/")
def get_root():
    return {"name": "ms-user", "data": "3"}
