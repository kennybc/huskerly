from core.chat.shared import check_chat_edit_perm, check_chat_exists_and_not_deleted, check_chat_view_perm, check_in_chat, join_chat
from core.organization import check_assist_admin_perm
from core.team import check_team_perm
from utils.error import UserError, ServerError
from utils.connect import get_cursor




def get_stream(current_user_email: str, stream_id: int) -> dict:
    with get_cursor() as cursor:
        if not check_chat_exists_and_not_deleted(stream_id):
            raise UserError("Stream does not exist or has been deleted")
        
        if not check_chat_view_perm(current_user_email, stream_id):
            raise UserError("User does not have permission to view this stream")
        
        cursor.execute(
            """
            SELECT c.name AS stream_name, cu.user_email
            FROM chats c
            JOIN chat_users cu ON c.id = cu.chat_id
            WHERE c.chat_type == 'STREAM' AND c.id = %s AND c.deleted = FALSE
            """, (stream_id,))

        result = cursor.fetchall()
        stream_info = {"stream_name": result[0][0],
                       "users": [row[1] for row in result]}
        return stream_info


def create_stream(stream_name: str, public: bool, creator_email: str, team_id: int) -> int:
    stream_id = None
    with get_cursor() as cursor:
        
        if not check_team_perm(creator_email, team_id):
            raise UserError("User does not have permission to create streams in this team")

        cursor.execute(
            """
            INSERT INTO chats (name, created_by_email, team_id, public, chat_type)
            VALUES (%s, %s, %s, %s, 'STREAM')
            """, (stream_name, creator_email, team_id, public))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            stream_id = cursor.fetchone()[0]
            print("created stream: ", stream_id)
        else:
            raise ServerError("Failed to create stream")
        
    if stream_id:
        join_chat(stream_id, creator_email, True)
    return stream_id


def edit_stream(current_user_email: str, stream_id: int, stream_name: str, public: bool):
    with get_cursor() as cursor:

        if not check_chat_edit_perm(current_user_email, stream_id):
            raise UserError(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE chats
            SET name = %s, public = %s
            WHERE id = %s AND chat_type = 'STREAM' AND deleted = FALSE
            """, (stream_name, public, stream_id))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to update stream")


def leave_stream(stream_id: int, current_user_email: str, user_email: str):
    with get_cursor() as cursor:
        
        if not check_chat_exists_and_not_deleted(stream_id):
            raise UserError("Stream does not exist or has been deleted")
        
        if not check_in_chat(user_email, stream_id):
            raise UserError("User is not in the stream")
            
        if not (check_assist_admin_perm(current_user_email, stream_id) or current_user_email == user_email):
            raise UserError("User does not have permission to perform this action")
        
        cursor.execute(
            """
            DELETE FROM chat_users
            WHERE chat_id = %s AND user_email = %s
            """, (stream_id, user_email))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to leave stream")


def delete_stream(current_user_email: str, stream_id: int):
    with get_cursor() as cursor:

        if not check_chat_edit_perm(current_user_email, stream_id):
            raise UserError("User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE chats
            SET deleted = TRUE
            WHERE id = %s
            """, (stream_id,))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to delete stream")
