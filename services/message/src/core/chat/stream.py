from core.chat.shared import check_in_chat, join_chat
from core.organization import check_assist_admin_perm
from utils.connect import get_cursor


def check_stream_perm(current_user_email: str, stream_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
                SELECT o.org_id
                FROM chats c
                JOIN teams t ON c.team_id = t.id
                JOIN organizations o ON t.organization_id = o.org_id
                WHERE c.id = %s
                """, (stream_id,))

        org_id = cursor.fetchone()[0]

        return not (check_in_chat(current_user_email, stream_id) or check_assist_admin_perm(current_user_email, org_id))


def get_stream(stream_id: int) -> dict:
    with get_cursor() as cursor:
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


def create_stream(stream_name: str, creator_email: str, team_id: int) -> int:
    with get_cursor() as cursor:
        stream_id = None

        cursor.execute(
            """
            INSERT INTO chats (name, created_by_email, team_id, chat_type)
            VALUES (%s, %s, %s, 'STREAM')
            """, (stream_name, creator_email, team_id))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            stream_id = cursor.fetchone()[0]
            join_chat(stream_id, creator_email)

        return stream_id


def edit_stream(current_user_email: str, stream_id: int, stream_name: str, public: bool) -> bool:
    with get_cursor() as cursor:

        if not check_stream_perm(current_user_email, stream_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE chats
            SET name = %s, public = %s
            WHERE id = %s AND chat_type = 'STREAM' AND deleted = FALSE
            """, (stream_name, public, stream_id))

        return cursor.rowcount == 1


def leave_stream(stream_id: int, current_user_email: str, user_email: str) -> bool:
    with get_cursor() as cursor:

        if not check_stream_perm(current_user_email, stream_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            DELETE FROM chat_users
            WHERE chat_id = %s AND user_email = %s
            """, (stream_id, user_email))

        return cursor.rowcount == 1


def delete_stream(current_user_email: str, stream_id: int) -> bool:
    with get_cursor() as cursor:

        if not check_stream_perm(current_user_email, stream_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE chats
            SET deleted = TRUE
            WHERE id = %s
            """, (stream_id,))

        return cursor.rowcount == 1
