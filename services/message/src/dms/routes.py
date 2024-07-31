from typing import Any
from fastapi import Body, APIRouter

from dms.handler import DMHandler

router = APIRouter()

handler = DMHandler()


@router.post("/ws/connect")
async def ws_connect(req: Any = Body(None)):
    handler.add_connection(req["connectionId"])
    return {"status": 200}


@router.post("/ws/disconnect")
async def ws_disconnect(req: Any = Body(None)):
    handler.remove_connection(req["connectionId"])
    return {"status": 200}


@router.post("/ws/unknown")
async def ws_unknown(req: Any = Body(None)):
    print(req)
    return {"status": 404}


@router.post("/ws/send")
async def ws_send(req: Any = Body(None)):
    handler.broadcast(req["payload"]["message"])
    return {"status": 200}
