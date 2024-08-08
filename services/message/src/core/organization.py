from typing import Optional
from utils.error import UserError, ServerError
from utils.connect import get_cursor
from utils.secrets import get_secrets
import requests

secrets = get_secrets()
api_endpoint = secrets["api_ep"]
org_user_endpoint, user_perm_endpoint = api_endpoint + "/user/org/", api_endpoint + "/user/permission/"

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
        response = requests.get(endpoint)
    else:
        print("getting user perms with org_id: ", user_email, org_id)
        endpoint = user_perm_endpoint + f"{user_email}/{org_id}"
        print("endpoint:", endpoint)
        response = requests.get(endpoint)
    print("response:", response.json())
    if not response or response.status_code != 200:
        raise ServerError("Failed to get user permissions")
    perm_level = response.json()['Permission']
    print("perm_level:", perm_level)
    return perm_level


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


def get_all_orgs(current_user_email: str) -> list:
    with get_cursor() as cursor:
        if not check_full_admin_perm(current_user_email):
            raise UserError(
                "User does not have permission to perform this action")
        
        cursor.execute(
            """
            SELECT id, name
            FROM organizations
            WHERE deleted = FALSE
            """
        )

        orgs = cursor.fetchall()
        return orgs


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
    
def demote_to_member(org_id: int, demoted_user_email: str, current_user_email: str):
    with get_cursor() as cursor:
        if not check_full_admin_perm(current_user_email, org_id):
            raise UserError(
                "User does not have permission to perform this action")

        print(
            "Demoting user with user_email:", demoted_user_email, "to member for org_id:", org_id
        )

        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")
        
        demote_endpoint = org_user_endpoint + f"{org_id}/demote"
        print("Demote endpoint:", demote_endpoint)
        payload = {
            "user_email": demoted_user_email,
            "target_role": "MEMBER"
        }
        
        try:
            response = requests.put(demote_endpoint, json=payload)
            print("Response:", response.json())
            if not response or response.status_code != 200:
                raise ServerError("Failed to demote user")
        except Exception:
            raise ServerError(f"""Failed to demote user""")
        
def promote_to_assist_admin(org_id: int, new_assist_admin_email: str, current_user_email: str):
    with get_cursor() as cursor:
        if not check_full_admin_perm(current_user_email, org_id):
            raise UserError(
                "User does not have permission to perform this action")

        print(
            "Promoting user with user_email:", new_assist_admin_email, "to assistant admin for org_id:", org_id
        )

        if not check_org_exists_and_not_deleted(org_id):
            raise UserError("Organization does not exist or has been deleted")
        
        promote_endpoint = org_user_endpoint + f"{org_id}/promote"
        print("Promote endpoint:", promote_endpoint)
        payload = {
            "user_email": new_assist_admin_email,
            "target_role": "ASSIST_ADMIN"
        }
        
        try:
            response = requests.put(promote_endpoint, json=payload)
            print("Response:", response.json())
            if not response or response.status_code != 200:
                raise ServerError("Failed to demote user")
        except Exception:
            raise ServerError(f"""Failed to demote user""")


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
        
        promote_endpoint = org_user_endpoint + f"{org_id}/promote"
        print("Promote endpoint:", promote_endpoint)
        payload = {
            "user_email": new_lead_admin_email,
            "target_role": "ORG_ADMIN"
        }
        
        try:
            response = requests.put(promote_endpoint, json=payload)
            print("Response:", response.json())
            if not response or response.status_code != 200:
                raise ServerError("Failed to transfer lead admin")
        except Exception:
            raise ServerError(f"""Failed to transfer lead admin""")
        


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

        org_info = {"name": result[0], "users": users, "user_count": len(users)}
        return org_info
