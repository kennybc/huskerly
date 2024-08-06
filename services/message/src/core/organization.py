from typing import Optional
from utils.error import UserError, ServerError
from utils.connect import get_cursor
from utils.secrets import get_secrets
import requests

secrets = get_secrets()
user_endpoint = secrets["user_ep"]
org_user_endpoint, user_perm_endpoint = user_endpoint + "org/", user_endpoint + "permission/"


def check_org_exists_and_not_deleted(org_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT deleted
            FROM organizations
            WHERE id = %s
            """, (org_id,),
        )

        result = cursor.fetchone()
        return result is not None and not result[0]


def get_perm_level(user_email: str, org_id: Optional[int] = None) -> str:
    if org_id is None:
        print("getting user perms without org_id: ", user_email)
        endpoint = user_perm_endpoint + f"{user_email}"
        print("endpoint:", endpoint)
        response = requests.get(endpoint).json()
    else:
        print("getting user perms with org_id: ", user_email, org_id)
        endpoint = user_perm_endpoint + f"{user_email}/{org_id}"
        print("endpoint:", endpoint)
        response = requests.get(endpoint).json()
    print("response:", response)
    if not response or response.status_code != 200:
        raise ServerError("Failed to get user permissions")
    perm_level = response['Permission']
    print("perm_level (type):", type(perm_level.json()))
    print("perm_level (value):", perm_level.json())
    return perm_level.json()


def check_org_perm_in(
    current_user_email, org_id: Optional[int] = None, acceptable_perms: list = []
) -> bool:
    perm_level = get_perm_level(current_user_email, org_id)
    print("Checking perm in:", perm_level, acceptable_perms)
    res = perm_level in acceptable_perms
    print("Result:", res)
    return res

def check_assist_admin_perm(
    current_user_email: str, org_id: Optional[int] = None
) -> bool:
    return check_org_perm_in(current_user_email, org_id, ['ASSIST_ADMIN', 'ORG_ADMIN', 'SYS_ADMIN'])


def check_full_admin_perm(
    current_user_email: str, org_id: Optional[int] = None
) -> bool:
    return check_org_perm_in(current_user_email, org_id, ['ORG_ADMIN', 'SYS_ADMIN'])

def check_in_org(user_email: str, org_id: int) -> bool:
    return get_perm_level(user_email, org_id) != "NONE"


def create_org(org_name: str, creator_email: str) -> int:
    with get_cursor() as cursor:
        org_id = None

        cursor.execute(
            """
            INSERT INTO organizations (name, created_by_email)
            VALUES (%s, %s)
            """, (org_name, creator_email),
        )

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            org_id = cursor.fetchone()[0]

        return org_id


def transfer_lead_admin(
    org_id: int, new_lead_admin_email: str, current_user_email: str
):
    with get_cursor() as cursor:
        if not check_full_admin_perm(current_user_email, org_id):
            raise UserError(
                "User does not have permission to perform this action")

        print(
            "Transferring lead admin for org_id:",
            org_id,
            "to new_lead_admin_email:",
            new_lead_admin_email,
        )

        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")
        
        promote_endpoint = org_user_endpoint + f"{org_id}/promote/"
        payload = {
            "user_email": new_lead_admin_email,
            "target_role": "ORG_ADMIN"
        }
        
        try:
            response = requests.post(promote_endpoint, json=payload)
            if not response or response.status_code != 200:
                raise ServerError("Failed to transfer lead admin")
        except Exception as e:
            raise ServerError(f"""Error occurred while transferring lead admin role: {
                          response.text}""") from e
        


def edit_org(org_id: int, current_user_email: str, org_name: str):
    with get_cursor() as cursor:
        print("Editing org with org_id:", org_id, "and org_name:", org_name)

        if not check_assist_admin_perm(current_user_email, org_id):
            raise UserError(
                "User does not have permission to perform this action")

        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")

        # Perform the update
        cursor.execute(
            """
            UPDATE organizations
            SET name = %s
            WHERE id = %s AND deleted = FALSE
            """,
            (org_name, org_id),
        )

        # print("Rowcount after update:", cursor.rowcount)

        if not cursor.rowcount == 1:
            print("Failed to update organization with org_id:", org_id)
            raise ServerError("Failed to update organization")


def delete_org(org_id: int, current_user_email: str):
    with get_cursor() as cursor:

        if not check_assist_admin_perm(current_user_email, org_id):
            raise UserError(
                "User does not have permission to perform this action")
            
        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")

        cursor.execute(
            """
            UPDATE organizations
            SET deleted = TRUE
            WHERE id = %s
            """, (org_id,),
        )
        
        if not cursor.rowcount == 1:
            raise ServerError("Failed to delete organization")


def get_org(org_id: int) -> dict:
    with get_cursor() as cursor:
        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")
        
        cursor.execute(
            """
            SELECT name
            FROM organizations
            WHERE id = %s AND deleted = FALSE
            """, (org_id,),
        )

        result = cursor.fetchone()
        if result is None:
            return {}

        response = requests.get(org_user_endpoint + f"{org_id}")
        if not response or response.status_code != 200:
            raise ServerError("Failed to get organization users")
        users = response.json()["Users"]

        org_info = {"Name": result[0], "Users": users}
        return org_info
