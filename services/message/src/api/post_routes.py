from typing import Any, List
from fastapi import Form, Body, APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from core import post
from utils.connect import get_cursor
import requests
import os

router = APIRouter(prefix="/post")

class CreatePostRequest(BaseModel):
    current_user_email: str
    chat_id: int
    content: str

@router.post("", response_model=dict, tags=['Public'])
async def create_post(
    current_user_email: str = Form(...),
    chat_id: int = Form(...),
    content: str = Form(...),
    files: List[UploadFile] = File(...)
):
    request = CreatePostRequest(
        current_user_email=current_user_email,
        chat_id=chat_id,
        content=content
    )
    
    post_id, attachment_ids = await post.create_post(request.current_user_email, request.chat_id, request.content, files)
    return {'Status': 'SUCCESS', "post_id": post_id, "attachment_ids": attachment_ids}

class EditPostRequest(BaseModel):
    current_user_email: str
    post_id: int
    content: str
    
@router.put("/{post_id}", response_model=dict, tags=['Public'])
def edit_post(post_id: int, request: EditPostRequest):
    post.edit_post(request.current_user_email, post_id, request.content)
    return {'Status': 'SUCCESS'}

class DeletePostRequest(BaseModel):
    current_user_email: str
    
@router.delete("/{post_id}", response_model=dict, tags=['Public'])
def delete_post(post_id: int, request: DeletePostRequest):
    post.delete_post(request.current_user_email, post_id)
    return {'Status': 'SUCCESS'}

@router.delete("/{post_id}/attachment/{attachment_id}", response_model=dict, tags=['Public'])
def remove_attachment(post_id: int, attachment_id: int, request: DeletePostRequest):
    post.remove_attachment(request.current_user_email, post_id, attachment_id)
    return {'Status': 'SUCCESS'}

# @router.post("/send")
# async def send_post(
#     user_email: str = Form(),
#     chat_id: str = Form(),
#     content: str = Form(),
#     files: List[UploadFile] = File(...),
# ):
#     files_data = []
#     data = {}
#     for file in files:
#         ext = os.path.splitext(file.filename)[1][1:]
#         if ext in aliases:
#             ext = aliases[ext]
#         if ext not in supported:
#             raise HTTPException(status_code=415)

#         if ext not in data:
#             data[ext] = []
#         files_data.append(
#             ("files", (file.filename, await file.read(), file.content_type))
#         )

#     distributions = requests.post(
#         "http://localhost:8001",
#         files=files_data,
#     )

#     with get_cursor() as cursor:
#         cursor.execute(
#             "INSERT INTO posts (user_email, chat_id, content) VALUES (%s, %s, %s)",
#             (user_email, chat_id, content),
#         )
#         post_id = cursor.lastrowid

#         for url in distributions:
#             cursor.execute(
#                 "INSERT INTO attachments (post_id, url) VALUES (%s, %s)",
#                 (post_id, url),
#             )


# @router.post("/test")
# def test_post(
#     files: List[UploadFile] = File(...),
# ):
#     print("ok")


# @router.post("/edit")
# def edit_post(req: Any = Body(None)):
#     with get_cursor() as cursor:
#         cursor.execute(
#             "UPDATE posts SET content = %s WHERE id = %s AND user_email = '%s'",
#             (req["content"], req["post_id"], req["user_email"]),
#         )


# @router.post("/delete")
# def delete_post(req: Any = Body(None)):
#     with get_cursor() as cursor:
#         cursor.execute(
#             "UPDATE posts SET deleted = true WHERE id = %s AND user_email = '%s'",
#             (req["post_id"], req["user_email"]),
#         )
