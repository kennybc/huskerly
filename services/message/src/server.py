from typing import Any
from fastapi import Body, FastAPI
from api import endpoints

app = FastAPI(root_path="/message", debug=True)
app.include_router(endpoints.router)

connections = []


@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "4"}


@app.post("/ws/connect")
async def ws_connect(req: Any = Body(None)):
    print(req)
    return {"status": 200}


@app.post("/ws/disconnect")
async def ws_disconnect(req: Any = Body(None)):
    print(req)
    return {"status": 200}


@app.post("/ws/unknown")
async def ws_unknown(req: Any = Body(None)):
    print(req)
    return {"status": 404}


@app.post("/ws/send")
async def ws_send(req: Any = Body(None)):
    print(req)
    return {"status": 200}
