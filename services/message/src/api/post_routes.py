from typing import Any
from fastapi import Body, APIRouter
from utils.connect import get_cursor

router = APIRouter(prefix="/post")


@router.post("/send")
def send_post(req: Any = Body(None)):
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO posts (user_email, chat_id, content) VALUES (%s, %s, %s)",
            (req["user_email"], req["chat_id"], req["content"]),
        )


@router.post("/edit")
def edit_post(req: Any = Body(None)):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE posts SET content = %s WHERE id = %s AND user_email = '%s'",
            (req["content"], req["post_id"], req["user_email"]),
        )


@router.post("/delete")
def delete_post(req: Any = Body(None)):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE posts SET deleted = true WHERE id = %s AND user_email = '%s'",
            (req["post_id"], req["user_email"]),
        )
