from typing import Any
from fastapi import Body, APIRouter

from dms.handler import MessageHandler

router = APIRouter()

handler = MessageHandler()


@router.post("/ws/connect")
async def ws_connect(req: Any = Body(None)):
    print("New connection -> " + req["connectionId"])
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

@router.post("/ws/joinChannel")
async def ws_joinChan(req: Any = Body(None)):
    print(req) 
    return {"status" : 200}
