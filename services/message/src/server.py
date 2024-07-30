from fastapi import Request, FastAPI

app = FastAPI()
connections = []

@app.get("/")
def get_root():
    return {"name": "ms-message", "data": "3"}

@app.get("/ws/connect")
async def ws_connect(req: Request):
    body = await req.json()
    print(body)

@app.get("/ws/disconnect")
async def ws_disconnect(req: Request):
    body = await req.json()
    print(body)

@app.get("/ws/send")
async def ws_send(req: Request):
    body = await req.json()
    print(body)