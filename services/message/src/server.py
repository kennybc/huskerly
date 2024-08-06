from fastapi import FastAPI

<<<<<<< HEAD
from services.message.src.api import message_routes as dm_routes
from api import org_routes, team_routes, post_routes
=======
from dms import routes as dm_routes
from api import org_routes, team_routes, post_routes, stream_routes
>>>>>>> ac009dd300831862820b5fdfd63a647fb27e95a7
from utils.connect import initialize_db_connection

app = FastAPI(root_path="/message", debug=True)
app.include_router(dm_routes.router)
app.include_router(stream_routes.router)
app.include_router(post_routes.router)
app.include_router(org_routes.router)
app.include_router(team_routes.router)

initialize_db_connection()


@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "4"}
