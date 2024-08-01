

from utils.connect import get_cursor


def register_org(org_name, creator_email):
    with get_cursor() as cursor:
        org_id = None

        cursor.execute(
            """
            INSERT INTO organizations (name, created_by_email, lead_admin_email)
            VALUES (%s, %s, %s)
            """, (org_name, creator_email, creator_email))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            org_id = cursor.fetchone()[0]

        return org_id
