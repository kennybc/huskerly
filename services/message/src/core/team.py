from utils.connect import get_cursor


def get_team_info(team_id: int) -> dict:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT t.name AS team_name, tu.user_email
            FROM teams t
            JOIN team_users tu ON t.id = tu.team_id
            WHERE t.id = %s AND t.deleted = FALSE
            """, (team_id,))

        result = cursor.fetchall()
        team_info = {"team_name": result[0][0],
                     "users": [row[1] for row in result]}
        return team_info


def create_team(team_name: str, creator_email: str, org_id: int) -> int:
    with get_cursor() as cursor:
        team_id = None

        cursor.execute(
            """
            INSERT INTO teams (name, created_by_email, organization_id)
            VALUES (%s, %s, %s)
            """, (team_name, creator_email, org_id))

        if cursor.rowcount == 1:
            cursor.execute("SELECT LAST_INSERT_ID()")
            team_id = cursor.fetchone()[0]
            join_team_user(team_id, creator_email)

        return team_id


def join_team_user(team_id: int, user_email: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT deleted
            FROM teams
            WHERE id = %s
            """, (team_id,))

        result = cursor.fetchone()
        if result is None or result[0]:
            return False

        cursor.execute(
            """
            INSERT INTO team_members (team_id, user_email)
            VALUES (%s, %s)
            """, (team_id, user_email))

        return cursor.rowcount == 1


def edit_team(team_id: int, team_name: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE teams
            SET name = %s
            WHERE id = %s AND deleted = FALSE
            """, (team_name, team_id))

        return cursor.rowcount == 1


def delete_team(team_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE teams
            SET deleted = TRUE
            WHERE id = %s
            """, (team_id,))
        return cursor.rowcount == 1
