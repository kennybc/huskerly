from typing import Any, List
from fastapi import Form, Body, APIRouter, File, UploadFile, HTTPException
from utils.connect import get_cursor
import requests
import os

router = APIRouter(prefix="/post")
aliases = {"jpeg": "jpg", "jpe": "jpg", "jif": "jpg", "jfif": "jpg", "jfi": "jpg"}
supported = ["pdf", "jpg", "png"]


@router.post("/send")
async def send_post(
    user_email: str = Form(),
    chat_id: str = Form(),
    content: str = Form(),
    files: List[UploadFile] = File(...),
):
    files_data = []
    data = {}
    for file in files:
        ext = os.path.splitext(file.filename)[1][1:]
        if ext in aliases:
            ext = aliases[ext]
        if ext not in supported:
            raise HTTPException(status_code=415)

        if ext not in data:
            data[ext] = []
        files_data.append(
            ("files", (file.filename, await file.read(), file.content_type))
        )

    distributions = requests.post(
        "http://localhost:8001",
        files=files_data,
    )

    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO posts (user_email, chat_id, content) VALUES (%s, %s, %s)",
            (user_email, chat_id, content),
        )
        post_id = cursor.lastrowid

        for url in distributions:
            cursor.execute(
                "INSERT INTO attachments (post_id, url) VALUES (%s, %s)",
                (post_id, url),
            )


@router.post("/test")
def test_post(
    files: List[UploadFile] = File(...),
):
    print("ok")


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
