

from typing import Optional
from utils.connect import get_cursor
from utils.aws import get_aws_secret
import requests

secrets = get_aws_secret("huskerly-secrets-message")
org_user_endpoint, user_perm_endpoint = secrets['org_user_ep'], secrets['user_perm_ep']


def get_perm_level(user_email: str, org_id: Optional[int] = None) -> str:
    if org_id is None:
        print("getting user perms without org_id: ", user_email)
        perm_level = requests.get(user_perm_endpoint + f"{user_email}")
    else:
        print("getting user perms with org_id: ", user_email, org_id)
        perm_level = requests.get(
            user_perm_endpoint + f"{user_email}/{org_id}")
    print("perm_level (type):", type(perm_level.json()))
    print("perm_level (value):", perm_level.json())
    return perm_level.json()


def check_assist_admin_perm(current_user_email: str, org_id: Optional[int] = None) -> bool:
    perm_level = get_perm_level(current_user_email, org_id)
    print("Checking assist admin perm for:", perm_level)
    res = perm_level in ['SYS_ADMIN', 'ORG_ADMIN', 'ASSIST_ADMIN']
    print("Result:", res)

    return res


def check_full_admin_perm(current_user_email: str, org_id: Optional[int] = None) -> bool:
    perm_level = get_perm_level(current_user_email, org_id)
    print("Checking full admin perm for:", perm_level)
    return perm_level in ['SYS_ADMIN', 'ORG_ADMIN']


def check_in_org(user_email: str, org_id: int) -> bool:
    return get_perm_level(user_email, org_id) == 'NONE'


def create_org(org_name: str, creator_email: str) -> int:
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


def transfer_lead_admin(org_id: int, new_lead_admin_email: str, current_user_email: str) -> bool:
    with get_cursor() as cursor:

        if not check_full_admin_perm(current_user_email, org_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE organizations
            SET lead_admin_email = %s
            WHERE id = %s AND deleted = FALSE
            """, (new_lead_admin_email, org_id))

        return cursor.rowcount == 1


def edit_org(org_id: int, current_user_email: str, org_name: str) -> bool:
    with get_cursor() as cursor:
        print("Editing org with org_id:", org_id, "and org_name:", org_name)

        if not check_assist_admin_perm(current_user_email, org_id):
            raise Exception(
                "User does not have permission to perform this action")

        print("User has permission to edit org")

        cursor.execute(
            """
            UPDATE organizations
            SET name = %s
            WHERE id = %s AND deleted = FALSE
            """, (org_name, org_id))

        print("Rowcount:", cursor.rowcount)

        return cursor.rowcount == 1


def delete_org(org_id: int, current_user_email: str) -> bool:
    with get_cursor() as cursor:

        if not check_assist_admin_perm(current_user_email, org_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE organizations
            SET deleted = TRUE
            WHERE id = %s
            """, (org_id,))
        return cursor.rowcount == 1


def get_org(org_id: int) -> dict:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT name, lead_admin_email
            FROM organizations
            WHERE id = %s AND deleted = FALSE
            """, (org_id,))

        result = cursor.fetchone()
        if result is None:
            return {}

        users = requests.get(org_user_endpoint + f"{org_id}")

        org_info = {"name": result[0],
                    "lead_admin_email": result[1],
                    "users": users.json()}
        return org_info
