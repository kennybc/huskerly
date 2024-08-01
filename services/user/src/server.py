from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import endpoints
from utils.connect import initialize_db_connection

app = FastAPI(root_path="/user", debug=True)

origins = [
    "http://localhost:3000",
    "https://master.d2a8ctqnn4cl7u.amplifyapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

initialize_db_connection()


@app.get("/")
def get_root():
    return {"name": "ms-user-test-3", "data": "3"}
