from core.organization import check_in_org, check_org_exists_and_not_deleted
from utils.error import UserError, ServerError
from utils.connect import get_cursor
from core.chat.shared import check_chat_exists_and_not_deleted, check_chat_view_perm, check_in_chat, get_posts, join_chat
from core.message import create_channel

    
def get_dm_posts(current_user_email: str, chat_id: int) -> dict:
    if not check_chat_view_perm(current_user_email, chat_id):
        raise UserError("User does not have permission to view this dm")
    return get_posts(chat_id)

def get_dm(current_user_email: str, dm_id: int) -> dict:
    with get_cursor() as cursor:
        if not check_chat_exists_and_not_deleted(dm_id):
            raise UserError("Stream does not exist or has been deleted")
        
        if not check_chat_view_perm(current_user_email, dm_id):
            raise UserError("User does not have permission to view this dm")
        
        cursor.execute(
            """
            SELECT c.name AS dm_name, cu.user_email
            FROM chats c
            JOIN chat_users cu ON c.id = cu.chat_id
            WHERE c.chat_type = 'DIRECT_MESSAGE' AND c.id = %s AND c.deleted = FALSE
            """, (dm_id,))

        result = cursor.fetchall()
        dm_info = {"dm_name": result[0][0],
                   "users": [row[1] for row in result]}
        return dm_info


def create_dm(creator_email: str, other_user_email: str, org_id: int) -> int:
    dm_id = None
    with get_cursor() as cursor:
        
        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")

        if not check_in_org(creator_email, org_id) or not check_in_org(other_user_email, org_id):
            raise UserError("One or both users not in given organization")

        dm_name = f"{creator_email} and {other_user_email}"
        
        public = False

        cursor.execute(
            """
            INSERT INTO chats (name, created_by_email, org_id, public, chat_type)
            VALUES (%s, %s, %s, %s, 'DIRECT_MESSAGE')
            """, (dm_name, creator_email, org_id, public))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            dm_id = cursor.fetchone()[0]
            print("created dm: ", dm_id) 
        else:
            raise ServerError("Failed to create direct message")
        
    if dm_id:
        # creates a channel for the websocket connection
        create_channel(dm_id)
        
        join_chat(dm_id, creator_email)
        join_chat(dm_id, other_user_email)
    return dm_id
