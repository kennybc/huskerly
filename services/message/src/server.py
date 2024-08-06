from fastapi import FastAPI

from api import org_routes, team_routes, post_routes, stream_routes, message_routes
from utils.connect import initialize_db_connection

app = FastAPI(root_path="/message", debug=True)
app.include_router(message_routes.router)
app.include_router(stream_routes.router)
app.include_router(post_routes.router)
app.include_router(org_routes.router)
app.include_router(team_routes.router)

initialize_db_connection()


@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "4"}