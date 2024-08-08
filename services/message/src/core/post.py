import os
from typing import List
from fastapi import File, UploadFile
import requests
from core.chat.shared import check_chat_edit_perm, get_org_id
from core.organization import check_assist_admin_perm
from utils.secrets import get_secrets
from utils.error import UserError, ServerError
from utils.connect import get_cursor

secrets = get_secrets()
api_endpoint = secrets["api_ep"]
upload_endpoint = api_endpoint + "/upload/"

aliases = {"jpeg": "jpg", "jpe": "jpg", "jif": "jpg", "jfif": "jpg", "jfi": "jpg"}
supported = ["pdf", "jpg", "png"]


def check_post_edit_perm(user_email: str, post_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT user_email, chat_id
            FROM posts
            WHERE id = %s
            """, (post_id,))
        result = cursor.fetchone()
        if not result:
            raise UserError("Post does not exist or has been deleted")
        poster_email, chat_id = result
        
        return poster_email == user_email or check_assist_admin_perm(user_email, get_org_id(chat_id))


async def process_files(files: List[UploadFile]) -> List[str]:
    files_data = []
    data = {}
    for file in files:
        ext = os.path.splitext(file.filename)[1][1:]
        if ext in aliases:
            ext = aliases[ext]
        if ext not in supported:
            raise UserError("Unsupported file type: " + ext)

        if ext not in data:
            data[ext] = []
        files_data.append(
            ("files", (file.filename, await file.read(), file.content_type))
        )

    distributions = requests.post(
        upload_endpoint,
        files=files_data,
    )
    
    return distributions


async def create_post(current_user_email: str, chat_id: int, content: str, files: List[UploadFile] = File(...)) -> int:
    post_id = None
    with get_cursor() as cursor:
        if not check_chat_edit_perm(current_user_email, chat_id):
            raise UserError("User does not have permission to create posts in this chat")
        
        cursor.execute(
            """
            INSERT INTO posts (content, chat_id, user_email)
            VALUES (%s, %s, %s)
            """, (content, chat_id, current_user_email))
        
        
        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            post_id = cursor.fetchone()[0]
            print("created stream: ", post_id)
        else:
            raise ServerError("Failed to create post")
        
    if post_id:
        distributions = process_files(files)
        with get_cursor() as cursor:
            for url in distributions:
                cursor.execute(
                    """
                    INSERT INTO attachments (post_id, url)
                    VALUES (%s, %s)
                    """, (post_id, url))
    return post_id
        

def edit_post(current_user_email: str, post_id: int, content: str):
    with get_cursor() as cursor:
        if not check_post_edit_perm(current_user_email, post_id):
            raise UserError("User does not have permission to edit this post")
        
        cursor.execute(
            """
            UPDATE posts
            SET content = %s, edited_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """, (content, post_id)
        )
        
        if not cursor.rowcount == 1:
            raise ServerError("Failed to update post")
            

def delete_post(current_user_email: str, post_id: int):
    with get_cursor() as cursor:
        if not check_post_edit_perm(current_user_email, post_id):
            raise UserError("User does not have permission to delete this post")
        
        cursor.execute(
            """
            UPDATE posts
            SET deleted = TRUE
            WHERE id = %s
            """, (post_id,)
        )
        
        if not cursor.rowcount == 1:
            raise ServerError("Failed to delete post")
        
def remove_attachment(current_user_email: str, post_id: int, url: str):
    with get_cursor() as cursor:
        if not check_post_edit_perm(current_user_email, post_id):
            raise UserError("User does not have permission to remove attachments from this post")
        
        cursor.execute(
            """
            DELETE FROM attachments
            WHERE post_id = %s AND url = %s
            """, (post_id, url)
        )
        
        if not cursor.rowcount == 1:
            raise ServerError("Failed to remove attachment")
        
    