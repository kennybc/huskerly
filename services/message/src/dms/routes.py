from typing import Any
from fastapi import Body, APIRouter

from dms.message import MessageHandler
from dms.connection import ConnectionHandler

router = APIRouter()

message_h = MessageHandler()
connect_h = ConnectionHandler()

@router.post("/ws/connect")
async def ws_connect(req: Any = Body(None)):
    print("New connection -> " + req["connectionId"])
    connect_h.add_connection(req["connectionId"])
    return {"status": 200}


@router.post("/ws/disconnect")
async def ws_disconnect(req: Any = Body(None)):
    connect_h.remove_connection(req["connectionId"])
    message_h.leave_channel(req["connectionId"])
    return {"status": 200}


@router.post("/ws/unknown")
async def ws_unknown(req: Any = Body(None)):
    print(req)
    return {"status": 404}


@router.post("/ws/send")
async def ws_send(req: Any = Body(None)):
    print("Attempting message from " + req["connectionId"])
    message_h.send_to_channel(req["connectionId"], req["payload"]["message"])


@router.post("/ws/joinChannel")
async def ws_joinChan(req: Any = Body(None)):
    status = message_h.join_channel(req["payload"]["channel_id"], req["connectionId"])
    return status
