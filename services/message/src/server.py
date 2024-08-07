from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import org_routes, team_routes, post_routes, stream_routes, message_routes, dm_routes
from utils.connect import initialize_db_connection
from utils.error import ServerError, UserError

app = FastAPI(root_path="/message", debug=True)
app.include_router(message_routes.router)
app.include_router(stream_routes.router)
app.include_router(dm_routes.router)
app.include_router(post_routes.router)
app.include_router(org_routes.router)
app.include_router(team_routes.router)

initialize_db_connection()

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


@app.exception_handler(UserError)
async def user_error_handler(request, exc: UserError):
    return JSONResponse(
        status_code=400,
        content={"status": "FAILED", "detail": exc.message},
    )


@app.exception_handler(ServerError)
async def server_error_handler(request, exc: ServerError):
    return JSONResponse(
        status_code=500,
        content={"status": "FAILED", "detail": exc.message},
    )


@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "4"}
