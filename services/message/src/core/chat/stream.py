from core.chat.shared import check_chat_edit_perm, check_chat_exists_and_not_deleted, check_chat_view_perm, check_in_chat, get_posts, join_chat
from core.organization import check_assist_admin_perm
from core.team import check_team_perm
from utils.error import UserError, ServerError
from utils.connect import get_cursor
from core.message import create_channel




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
            WHERE c.chat_type = 'STREAM' AND c.id = %s AND c.deleted = FALSE
            """, (stream_id,))

        result = cursor.fetchall()
        stream_info = {"stream_name": result[0][0],
                       "users": [row[1] for row in result]}
        return stream_info
    
    
def get_stream_posts(current_user_email: str, stream_id: int) -> dict:
    if not check_chat_view_perm(current_user_email, stream_id):
        raise UserError("User does not have permission to view this stream")
    
    return get_posts(stream_id)

def join_stream(stream_id: int, user_email: str):
    if not check_chat_view_perm(user_email, stream_id):
        raise UserError("User does not have permission to join this stream")

    return join_chat(stream_id, user_email)


def create_stream(stream_name: str, public: bool, creator_email: str, team_id: int) -> int:
    stream_id = None
    with get_cursor() as cursor:
        print("creating stream: ", stream_name, public, creator_email, team_id)
        if not check_team_perm(creator_email, team_id):
            raise UserError("User does not have permission to create streams in this team")
        
        print(type(public))
        
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
        # creates a channel for the websocket connection
        create_channel(stream_id)
        
        join_chat(stream_id, creator_email)
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
        
def join_stream(stream_id: int, user_email: str):
    team_id = None
    with get_cursor() as cursor:
        print("Joining stream: ", stream_id, user_email)
        cursor.execute(
            """
            SELECT team_id
            FROM chats
            WHERE id = %s AND chat_type = 'STREAM' AND deleted = FALSE
            """, (stream_id,))
        
        result = cursor.fetchone()
        if result is None:
            raise ServerError("Failed to join stream")
        
        team_id = result[0]
        print("Team ID:", team_id)
        
        if not check_team_perm(user_email, team_id):
            raise UserError("User must be in the team to join the stream")
        
    if team_id:
        join_chat(stream_id, user_email)

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
