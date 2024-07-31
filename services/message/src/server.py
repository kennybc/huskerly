from fastapi import FastAPI

from dms import routes as dm_routes
from utils.connect import initialize_db_connection

app = FastAPI(root_path="/message", debug=True)
app.include_router(dm_routes.router)

initialize_db_connection()


@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "4"}
