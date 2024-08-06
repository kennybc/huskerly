
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import user_routes, org_routes
from utils.connect import initialize_db_connection
from utils.error import ServerError, UserError

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

app.include_router(user_routes.router)
app.include_router(org_routes.router)


@app.exception_handler(UserError)
async def user_error_handler(request, exc: UserError):
    return JSONResponse(
        status_code=400,
        content={"Status": "FAILED", "Detail": exc.message},
    )


@app.exception_handler(ServerError)
async def server_error_handler(request, exc: ServerError):
    return JSONResponse(
        status_code=500,
        content={"Status": "FAILED", "Detail": exc.message},
    )


initialize_db_connection()


# @app.get("/")
# def get_root():
#     return {"name": "ms-user-test-3", "data": "3"}
