from utils.connect import get_cursor


def get_post_history(chat_id: int) -> dict:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT p.id, p.content, p.created_at, p.edited_at, p.user_email
            FROM posts p
            JOIN chats c ON p.chat_id = c.id
            WHERE p.chat_id = %s AND c.deleted = FALSE
            """, (chat_id,))

        result = cursor.fetchall()
        post_history = [{"id": row[0],
                         "content": row[1],
                         "created_at": row[2],
                         "edited_at": row[3],
                         "user_email": row[4]} for row in result]
        return post_history


def join_chat(chat_id: int, user_email: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT deleted
            FROM chats
            WHERE id = %s
            """, (chat_id,))

        result = cursor.fetchone()
        if result is None or result[0]:
            return False

        cursor.execute(
            """
            INSERT INTO chat_users (chat_id, user_email)
            VALUES (%s, %s)
            """, (chat_id, user_email))

        return cursor.rowcount == 1


def delete_chat(chat_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE chats
            SET deleted = TRUE
            WHERE id = %s
            """, (chat_id,))
        return cursor.rowcount == 1
