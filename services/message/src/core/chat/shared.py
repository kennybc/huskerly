from core.organization import check_assist_admin_perm
from utils.error import UserError, ServerError
from utils.connect import get_cursor
    
def check_chat_exists_and_not_deleted(chat_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT deleted
            FROM chats
            WHERE id = %s
            """, (chat_id,))

        result = cursor.fetchone()
        return result is not None and not result[0]
    
def check_in_chat(user_email: str, chat_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT user_email
            FROM chat_users
            WHERE user_email = %s AND chat_id = %s
            """, (user_email, chat_id))

        return cursor.fetchone() is not None
    
def get_chat_type(chat_id: int) -> str:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT chat_type
            FROM chats
            WHERE id = %s
            """, (chat_id,))

        result = cursor.fetchone()
        return result[0] if result else None
    
def get_org_id(chat_id: int) -> int:
    with get_cursor() as cursor:
        chat_type = get_chat_type(chat_id)
        org_id = None
        if chat_type == "DIRECT_MESSAGE":
            cursor.execute(
                """
                SELECT org_id
                FROM chats
                WHERE id = %s
                """, (chat_id,))
            result = cursor.fetchone()
            org_id = result[0] if result else None
        elif chat_type == "STREAM":
            cursor.execute(
                """
                SELECT t.org_id
                FROM teams t
                JOIN chats c ON t.id = c.team_id
                WHERE c.id = %s
                """, (chat_id,))
            result = cursor.fetchone()
            org_id = result[0] if result else None
        return org_id

    
def check_chat_edit_perm(current_user_email: str, chat_id: int) -> bool:
    with get_cursor() as _:
        print("Checking chat edit permission for user:", current_user_email, "and chat_id:", chat_id)
        org_id = get_org_id(chat_id)
        print("checking chat view perm:", check_in_chat(current_user_email, chat_id), check_assist_admin_perm(current_user_email, org_id))
        return check_in_chat(current_user_email, chat_id) or check_assist_admin_perm(current_user_email, org_id)
    
def check_chat_view_perm(current_user_email: str, chat_id: int) -> bool:
    with get_cursor() as cursor:
        print("Checking chat view permission for user:", current_user_email, "and chat_id:", chat_id) 
        cursor.execute(
            """
                SELECT public
                FROM chats
                WHERE id = %s
                """, (chat_id,))
        result = cursor.fetchone()
        public = result[0] if result else False
        print("public:", public)
        
        return public or check_chat_edit_perm(current_user_email, chat_id)
    

def get_posts(chat_id: int) -> dict:
    with get_cursor() as cursor:
        if not check_chat_exists_and_not_deleted(chat_id):
            raise UserError("Chat does not exist or has been deleted")
        
        # if not check_chat_view_perm(current_user_email, chat_id):
        #     raise UserError("User does not have permission to view this chat")
        
        cursor.execute(
            """
            SELECT p.id, p.content, p.created_date, p.edited_at, p.user_email
            FROM posts p
            JOIN chats c ON p.chat_id = c.id
            WHERE p.chat_id = %s AND c.deleted = FALSE AND p.deleted = FALSE
            """, (chat_id,)) #TODO: add attachments here

        result = cursor.fetchall()
        post_history = [{"id": row[0],
                         "content": row[1],
                         "created_date": row[2],
                         "edited_date": row[3],
                         "user_email": row[4]} for row in result]
        return post_history


def join_chat(chat_id: int, user_email: str):
    with get_cursor() as cursor:
        if not check_chat_exists_and_not_deleted(chat_id):
            raise UserError("Chat does not exist or has been deleted")
        
        # if not override_visibility_perm and not check_chat_view_perm(user_email, chat_id):
        #     raise UserError("User does not have permission to view this chat")
        
        if check_in_chat(user_email, chat_id):
            raise UserError("User is already in this chat")

        cursor.execute(
            """
            INSERT INTO chat_users (chat_id, user_email)
            VALUES (%s, %s)
            """, (chat_id, user_email))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to join chat")

