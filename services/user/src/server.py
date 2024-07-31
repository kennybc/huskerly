from fastapi import FastAPI
from api import endpoints
from utils.connect import initialize_db_connection

app = FastAPI(root_path="/user", debug=True)

app.include_router(endpoints.router)

initialize_db_connection()


@app.get("/")
def get_root():
    return {"name": "ms-user-test-3", "data": "3"}
