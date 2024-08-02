from utils.connect import get_cursor
from core.chat.shared import join_chat


def get_dm_info(dm_id: int) -> dict:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT c.name AS dm_name, cu.user_email
            FROM chats c
            JOIN chat_users cu ON c.id = cu.chat_id
            WHERE c.chat_type == 'DIRECT_MESSAGE' AND c.id = %s AND c.deleted = FALSE
            """, (dm_id,))

        result = cursor.fetchall()
        dm_info = {"dm_name": result[0][0],
                   "users": [row[1] for row in result]}
        return dm_info


def create_dm(creator_email: str, other_user_email: str, org_id: int) -> int:
    with get_cursor() as cursor:
        dm_id = None

        dm_name = f"{creator_email} and {other_user_email}"

        cursor.execute(
            """
            INSERT INTO chats (name, created_by_email, org_id, chat_type)
            VALUES (%s, %s, %s, 'DIRECT_MESSAGE')
            """, (dm_name, creator_email, org_id))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            dm_id = cursor.fetchone()[0]
            join_chat(dm_id, creator_email)
            join_chat(dm_id, other_user_email)

        return dm_id


def edit_dm(dm_id: int, dm_name: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE chats
            SET name = %s
            WHERE id = %s AND chat_type = 'DIRECT_MESSAGE' AND deleted = FALSE
            """, (dm_name, dm_id))

        return cursor.rowcount == 1
