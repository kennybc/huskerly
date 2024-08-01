from utils.connect import get_cursor


def send_post(user_email, chat_id, content):
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO posts (user_email, chat_id, content) VALUES (%s, %s, %s)",
            (user_email, chat_id, content),
        )


def edit_post(user_email, post_id, content):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE posts SET content = %s WHERE id = %s AND user_email = '%s'",
            (content, post_id, user_email),
        )


def delete_post(user_email, post_id):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE posts SET deleted = true WHERE id = %s AND user_email = '%s'",
            (post_id, user_email),
        )
