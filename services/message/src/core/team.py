
from core.organization import check_assist_admin_perm, check_in_org
from utils.error import ServerError, UserError
from utils.connect import get_cursor


def check_in_team(user_email: str, team_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT user_email
            FROM team_users
            WHERE user_email = %s AND team_id = %s
            """, (user_email, team_id))

        return cursor.fetchone() is not None


def check_team_perm(current_user_email: str, team_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
                SELECT t.org_id
                FROM teams t
                WHERE t.id = %s AND t.deleted = FALSE
                """, (team_id,))
        
        row = cursor.fetchone() 
        if not row:
            return False

        org_id = row[0]

        return (check_in_team(current_user_email, team_id) or check_assist_admin_perm(current_user_email, org_id))
    
def check_team_exists_and_not_deleted(team_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT deleted
            FROM teams
            WHERE id = %s
            """, (team_id,))

        result = cursor.fetchone()
        return result is not None and not result[0]


def get_team(team_id: int) -> dict:
    with get_cursor() as cursor:
        if not check_team_exists_and_not_deleted(team_id):
            raise UserError("Team does not exist or has been deleted")
        
        team_info = {}
        
        cursor.execute(
            """
            SELECT name
            FROM teams
            WHERE id = %s AND deleted = FALSE
            """, (team_id,))
        
        team_name = cursor.fetchone()[0]
        team_info["team_name"] = team_name
        team_info["users"] = []
        
        cursor.execute(
            """
            SELECT t.name AS team_name, tu.user_email
            FROM teams t
            JOIN team_users tu ON t.id = tu.team_id
            WHERE t.id = %s AND t.deleted = FALSE
            """, (team_id,))
        
        
        for row in cursor.fetchall():
            print(row)
            team_name, user_email = row
            team_info["users"].append(user_email)
        print("Team info:", team_info)
        
        return team_info


def create_team(team_name: str, creator_email: str, org_id: int) -> int:
    team_id = None
    with get_cursor() as cursor:
        
        print("Creating team:", team_name, creator_email, org_id)
        cursor.execute(
            """
            INSERT INTO teams (name, created_by_email, org_id)
            VALUES (%s, %s, %s)
            """, (team_name, creator_email, org_id))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            team_id = cursor.fetchone()[0]
            print("Team ID:", team_id)
            
        else:
            raise ServerError("Failed to create team")
    if team_id:
        join_team(team_id, creator_email)
        print("Team joined")
    return team_id


def join_team(team_id: int, team_user_email: str):
    with get_cursor() as cursor:
        print("Joining team:", team_id, team_user_email)

        # Check if the team exists and is not deleted
        if not check_team_exists_and_not_deleted(team_id):
            raise UserError("Team does not exist or has been deleted")
        
        cursor.execute(
            """
            SELECT deleted, org_id
            FROM teams
            WHERE id = %s
            """, (team_id,))

        result = cursor.fetchone()
        print("selected team:", result)
        if result is None or result[0]:
            raise UserError("Team does not exist or has been deleted")

        org_id = result[1]

        # Check if the user is in the organization
        if not check_in_org(team_user_email, org_id):
            raise Exception("User is not in this organization")

        cursor.execute(
            """
            INSERT INTO team_users (team_id, user_email)
            VALUES (%s, %s)
            """, (team_id, team_user_email))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to join team")

def leave_team(team_id: int, current_user_email: str, team_user_email: str):
    with get_cursor() as cursor:
        if not check_team_exists_and_not_deleted(team_id):
            raise UserError("Team does not exist or has been deleted")

        if not check_team_perm(current_user_email, team_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            DELETE FROM team_users
            WHERE team_id = %s AND user_email = %s
            """, (team_id, team_user_email))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to leave team")


def edit_team(team_id: int, current_user_email: str, team_name: str):
    with get_cursor() as cursor:
        if not check_team_exists_and_not_deleted(team_id):
            raise UserError("Team does not exist or has been deleted")

        if not check_team_perm(current_user_email, team_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE teams
            SET name = %s
            WHERE id = %s AND deleted = FALSE
            """, (team_name, team_id))

        if not cursor.rowcount == 1:
            raise ServerError("Failed to update team")


def delete_team(current_user_email: str, team_id: int):
    with get_cursor() as cursor:
        if not check_team_exists_and_not_deleted(team_id):
            raise UserError("Team does not exist or has been deleted")

        if not check_team_perm(current_user_email, team_id):
            raise Exception(
                "User does not have permission to perform this action")

        cursor.execute(
            """
            UPDATE teams
            SET deleted = TRUE
            WHERE id = %s
            """, (team_id,))
        if not cursor.rowcount == 1:
            raise ServerError("Failed to delete team")
