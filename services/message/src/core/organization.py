

from utils.connect import get_cursor


def register_org(org_name: str, creator_email: str) -> int:
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


def modify_org(org_id: int, org_name: str, lead_admin_email: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE organizations
            SET name = %s, lead_admin_email = %s
            WHERE id = %s AND deleted = FALSE
            """, (org_name, lead_admin_email, org_id))

        return cursor.rowcount == 1


def delete_org(org_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE organizations
            SET deleted = TRUE
            WHERE id = %s
            """, (org_id,))
        return cursor.rowcount == 1


def get_org_info(org_id: int) -> dict:
    # TODO: get users from cognito?? :(
    return {}
