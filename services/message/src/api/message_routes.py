from typing import Any
from fastapi import Body, APIRouter

from core.message import add_connection, remove_connection, send_to_channel, join_channel, create_channel

router = APIRouter(prefix="/ws")


@router.post("/connect")
async def ws_connect(req: Any = Body(None)):
    print("New connection -> " + req["connectionId"])
    add_connection(req["connectionId"])
    return {"status": 200}


@router.post("/disconnect")
async def ws_disconnect(req: Any = Body(None)):
    remove_connection(req["connectionId"])
    return {"status": 200}


@router.post("/unknown")
async def ws_unknown(req: Any = Body(None)):
    print(req)
    return {"status": 404}


@router.post("/send")
async def ws_send(req: Any = Body(None)):
    print("\nAttempting message from " + req["connectionId"])
    send_to_channel(req["connectionId"], req["payload"]["message"])
    return {"status" : 200}


@router.post("/joinChannel")
async def ws_joinChan(req: Any = Body(None)):
    # join channel takes the unique channel id, the user's email, and the user's connection id
    status = join_channel(req["payload"]["channel_id"], req["payload"]["user_email"], req["connectionId"])
    return status

# Testing only
@router.post("/createChannel")
async def ws_createChan(req: Any = Body(None)):
    create_channel(req["payload"]["channel_id"])