from core.chat.shared import check_chat_edit_perm, get_org_id
from core.organization import check_assist_admin_perm
from utils.error import UserError, ServerError
from utils.connect import get_cursor

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

def create_post(current_user_email: str, chat_id: int, content: str) -> int:
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
        
    