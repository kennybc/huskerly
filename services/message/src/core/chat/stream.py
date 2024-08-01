from core.chat.shared import join_chat
from utils.connect import get_cursor


def get_stream_info(stream_id: int) -> dict:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT c.name AS stream_name, cu.user_email
            FROM chats c
            JOIN chat_users cu ON c.id = cu.chat_id
            WHERE c.chat_type == 'STREAM' AND c.id = %s
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


def edit_stream(stream_id: int, stream_name: str, public: bool) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE chats
            SET name = %s, public = %s
            WHERE id = %s AND chat_type = 'STREAM'
            """, (stream_name, public, stream_id))

        return cursor.rowcount == 1
