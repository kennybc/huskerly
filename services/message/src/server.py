from fastapi import Request, FastAPI

app = FastAPI(root_path="/message")
connections = []

@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "4"}

@app.post("/ws/connect")
async def ws_connect(req: Request):
    body = await req.json()
    print(body)
    return {"status": 200}

@app.post("/ws/disconnect")
async def ws_disconnect(req: Request):
    body = await req.json()
    print(body)
    return {"status": 200}

@app.post("/ws/send")
async def ws_send(req: Request):
    body = await req.json()
    print(body)
    return {"status": 200}