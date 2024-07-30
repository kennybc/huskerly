from fastapi import FastAPI
from api import endpoints

app = FastAPI(root_path="/user")

app.include_router(endpoints.router)


@app.get("/")
def get_root():
    return {"name": "ms-user-test-3", "data": "3"}
