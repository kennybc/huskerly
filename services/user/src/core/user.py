from utils.connect import get_cursor
from utils.aws import get_session, get_aws_secret
from datetime import datetime, timedelta
from typing import List, Optional
import requests

secrets = get_aws_secret("huskerly-secrets-user")

pool_id, create_org_endpoint = secrets["user_pool_id"], secrets["create_org_ep"]


def get_all_users_from_userpool_with_org_id(org_id, user_pool_id=pool_id):
    # Create a Cognito Identity Provider client
    session = get_session()
    client = session.client('cognito-idp', region_name='us-east-2')

    all_users = []
    pagination_token = None

    # Loop to handle pagination
    while True:
        # If there's a pagination token, include it in the request
        if pagination_token:
            response = client.list_users(
                UserPoolId=user_pool_id,
                PaginationToken=pagination_token
            )
        else:
            response = client.list_users(UserPoolId=user_pool_id)

        # Extend the all_users list with the current batch of users
        all_users.extend(response.get('Users', []))

        # Update the pagination token
        pagination_token = response.get('PaginationToken')

        # Break the loop if there's no more pagination token
        if not pagination_token:
            break

    # Filter users based on the custom:OrgId attribute
    filtered_users = [
        user for user in all_users
        if any(attr['Name'] == 'custom:OrgId' and attr['Value'] == str(org_id) for attr in user['Attributes'])
    ]

    org_admin = list(filter(
        lambda user: user['Attributes']['custom:OrgId'] == 'ORG_ADMIN', filtered_users))[0]
    assist_admins = list(filter(
        lambda user: user['Attributes']['custom:OrgId'] == 'ASSIST_ADMIN', filtered_users))
    members = list(filter(
        lambda user: user['Attributes']['custom:OrgId'] == 'MEMBER', filtered_users))
    other_users = list(filter(
        lambda user: user['Attributes']['custom:OrgId'] not in ['ORG_ADMIN', 'ASSIST_ADMIN', 'MEMBER'], filtered_users))

    return {
        'org_admin': org_admin,
        'assist_admins': assist_admins,
        'members': members,
        'other_users': other_users
    }


def get_user_from_userpool(username, user_pool_id=pool_id):
    # Create a Cognito Identity Provider client
    session = get_session()
    client = session.client('cognito-idp', region_name='us-east-2')

    # Get the user
    response = client.admin_get_user(
        UserPoolId=user_pool_id,
        Username=username
    )

    return response


def get_user_attributes(user_response):
    res = {attr['Name']: attr['Value']
           for attr in user_response['UserAttributes']}
    return res


def get_user_permission_level(user_email: str, org_id: Optional[int] = None):
    """
    Determines the permission level of a user within an organization.

    Parameters:
    user_email (str): The email of the user whose permissions are being checked.
    org_id (int, optional): The ID of the organization to check permission level in.

    Returns:
    str: The permission level of the user. Possible values are "SYS_ADMIN", "ORG_ADMIN", "ASSIST_ADMIN", "MEMBER", or "NONE".

    Raises:
    Exception: If the user cannot be verified in Cognito or if the user is not authorized to invite to the organization.
    """
    session = get_session()
    client = session.client('cognito-idp', region_name='us-east-2')

    # TODO:
    # if (access_token):
    #     print("Inviter token supplied, accessing user with token")
    #     response = client.get_user(
    #         AccessToken=access_token
    #     )
    # else:
    print(
        "WARNING: auth token not supplied, accessing user through admin API (needs to be fixed)")
    response = client.admin_get_user(
        UserPoolId=pool_id,
        Username=user_email
    )

    if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
        raise Exception(f"Failed to verify user {user_email} in Cognito.")

    user_attributes = get_user_attributes(response)

    if user_attributes.get('custom:SystemAdmin') == '1':
        return "SYS_ADMIN"
    elif user_attributes.get('custom:OrgId') and org_id and int(user_attributes.get('custom:OrgId')) == org_id and user_attributes.get('custom:UserStatus') == 'JOINED':
        return user_attributes.get('custom:OrgRoll')  # NEEDS TO BE FIXED
    else:
        return "NONE"


def promote_assist_admin_to_admin(org_id: int, user_email: str) -> bool:
    session = get_session()
    client = session.client('cognito-idp', region_name='us-east-2')

    current_role = get_user_permission_level(user_email, org_id)
    current_org_admin_email = get_all_users_from_userpool_with_org_id(org_id)[
        'org_admin']['email']

    if current_role == 'ASSIST_ADMIN':
        client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=user_email,
            UserAttributes=[
                {
                    'Name': 'custom:OrgRoll',
                    'Value': 'ORG_ADMIN'
                }
            ]
        )
        client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=current_org_admin_email,
            UserAttributes=[
                {
                    'Name': 'custom:OrgRoll',
                    'Value': 'ASSIST_ADMIN'
                }
            ]
        )
        return True
    else:
        raise Exception(f"""Error while promoting user {
                        user_email} to organization admin.""")


def promote_member_to_assist_admin(org_id: int, user_email: str) -> bool:
    session = get_session()
    client = session.client('cognito-idp', region_name='us-east-2')

    current_role = get_user_permission_level(user_email, org_id)
    if current_role == 'MEMBER':
        client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=user_email,
            UserAttributes=[
                {
                    'Name': 'custom:OrgRoll',
                    'Value': 'ASSIST_ADMIN'
                }
            ]
        )
        return True
    else:
        raise Exception(f"""Error while promoting user {
                        user_email} to assist admin.""")


def promote_user(org_id: int, user_email: str, target_role: str) -> bool:
    if target_role == 'ORG_ADMIN':
        return promote_assist_admin_to_admin(org_id, user_email)
    elif target_role == 'ASSIST_ADMIN':
        return promote_member_to_assist_admin(org_id, user_email)
    else:
        raise Exception(f"""Invalid role {target_role} provided.""")


def demote_to_member(org_id: int, user_email: str) -> bool:
    session = get_session()
    client = session.client('cognito-idp', region_name='us-east-2')

    current_role = get_user_permission_level(user_email, org_id)

    if current_role == 'SYS_ADMIN':
        raise Exception(f"""Cannot demote user {user_email} to member.""")
    elif current_role in ['ORG_ADMIN', 'ASSIST_ADMIN']:
        client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=user_email,
            UserAttributes=[
                {
                    'Name': 'custom:OrgRoll',
                    'Value': 'MEMBER'
                }
            ])
        return True
    else:
        raise Exception(f"""Error while demoting user {
                        user_email} to member.""")


def request_org(org_name: str, creator_email: str) -> bool:
    with get_cursor() as cursor:
        user = get_user_from_userpool(creator_email)
        if user is None:
            raise Exception(f"""User {creator_email} does not exist.""")
        user_attributes = get_user_attributes(user)
        if user_attributes.get('custom:UserStatus') == 'JOINED':
            raise Exception(
                f"""User {creator_email} is already a member of an organization.""")

        cursor.execute(
            """
            INSERT INTO organization_requests (org_name, created_by_email)
            VALUES (%s, %s)
            """, (org_name, creator_email))

        return cursor.rowcount == 1


def create_org(org_name: str, current_user_email: str) -> int:
    payload = {
        "org_name": org_name,
        "creator_email": current_user_email
    }

    response = requests.post(create_org_endpoint, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        org_id = response_data.get("org_id")
        # org_id = response_data
        if org_id:
            return int(org_id)
        else:
            raise ValueError("org_id not found in the response")
    else:
        response.raise_for_status()


def update_org_request(org_name: str, creator_email: str, current_user_email: str, status: str) -> bool:
    with get_cursor() as cursor:
        if get_user_permission_level(current_user_email) != "SYS_ADMIN":
            raise Exception(
                f"""User {current_user_email} is not authorized to update organization requests.""")

        cursor.execute(
            """
            SELECT created_by_email FROM organization_requests
            WHERE org_name = %s AND status = 'PENDING' AND created_by_email = %s
            """, (org_name, creator_email)
        )
        created_by_email = cursor.fetchone()[0]

        if created_by_email is None:
            raise ValueError(f"""Organization request for {
                             org_name} does not exist.""")

        if status == "APPROVED":
            cursor.execute(
                """
            UPDATE organization_requests
            SET status = 'APPROVED'
            WHERE org_name = %s AND created_by_email = %s AND status = 'PENDING'
            """, (org_name, creator_email))

            # cursor.execute(
            #     """
            # UPDATE organization_requests
            # SET status = 'REJECTED'
            # WHERE org_name = %s AND created_by_email != %s AND status = 'PENDING'
            # """, (org_name, creator_email)
            # )

            org_id = create_org(org_name, creator_email)
            if not invite_org(org_id, creator_email, current_user_email):
                return False

            if not join_org(org_id, creator_email, 'ORG_ADMIN'):
                return False
        elif status == "REJECTED":
            cursor.execute(
                """
            UPDATE organization_requests
            SET status = 'REJECTED'
            WHERE org_name = %s AND created_by_email = %s AND status = 'PENDING'
            """, (org_name, creator_email))
        else:
            raise ValueError(f"""Invalid status {status} provided.""")

        return True


def list_invites(user_email: str) -> List[dict]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM organization_invites
            WHERE user_email = %s;
            """, (user_email,))
        invites = cursor.fetchall()
        return invites


def join_org(org_id: int, user_email: str, role: str = 'MEMBER') -> bool:
    with get_cursor() as cursor:
        # Check if the user is already a member of an organization
        invited_user = get_user_from_userpool(user_email)
        user_attributes = get_user_attributes(invited_user)

        if user_attributes.get('custom:UserStatus') == 'JOINED':
            raise Exception(
                f"""User {user_email} is already a member of an organization.""")

        # Check if an invitation exists
        cursor.execute(
            """
            SELECT expiration_date, active FROM organization_invites
            WHERE org_id = %s AND user_email = %s;
            """, (org_id, user_email))

        invite = cursor.fetchone()

        if invite is None:
            raise Exception(f"""No invitation found for user {
                            user_email} to join organization {org_id}.""")

        expiration_date, active = invite

        # Check if the invitation is active and has not expired
        if not active:
            raise Exception(f"""The invitation for user {
                            user_email} to join organization {org_id} is not active.""")

        if datetime.now() > expiration_date:
            raise Exception(f"""The invitation for user {
                            user_email} to join organization {org_id} has expired.""")

        # Update the invitation to inactive
        cursor.execute(
            """
            UPDATE organization_invites
            SET active = FALSE
            WHERE org_id = %s AND user_email = %s;
            """, (org_id, user_email))

        # Update the user attribute in Cognito with the organization ID
        session = get_session()
        client = session.client('cognito-idp', region_name='us-east-2')

        response = client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=user_email,
            UserAttributes=[
                {
                    'Name': 'custom:UserStatus',
                    'Value': 'JOINED'
                },
                {
                    'Name': 'custom:OrgId',
                    'Value': str(org_id)
                },
                {
                    'Name': 'custom:OrgRoll',  # TODO: NEEDS TO BE FIXED
                    'Value': role
                }
            ]
        )

        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
            raise Exception(f"""Failed to update user {
                            user_email} with organization {org_id} in Cognito.""")

        return True


def invite_org(org_id: int, invitee_email: str, inviter_email: str, lifetime: int = 86400) -> bool:
    with get_cursor() as cursor:
        inviter = get_user_from_userpool(inviter_email)
        if inviter is None:
            raise Exception(
                f"""User {inviter_email} that created this invite does not exist.""")

        # Check if inviter is sysadmin or is in org
        if get_user_permission_level(inviter_email, org_id) not in ["SYS_ADMIN", "ORG_ADMIN", "ASSIST_ADMIN"]:
            raise Exception(
                f"""user {inviter_email} is not authorized to invite to this organization.""")

        # invitee = get_user_from_userpool(invitee_email)
        # if invitee is None:
        #     raise Exception(f"""Invited user {
        #                     invitee_email} does not exist.""")

        # Calculate expiration date
        expiration_date = datetime.now() + timedelta(seconds=lifetime)

        # Insert invite into the database
        cursor.execute(
            """
            INSERT INTO organization_invites (org_id, user_email, created_by_email, expiration_date)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE expiration_date = VALUES(expiration_date);
            """, (org_id, invitee_email, inviter_email, expiration_date))

        return cursor.rowcount == 1


def list_org_requests():
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM organization_requests
            WHERE status = 'PENDING';
            """
        )
        requests = cursor.fetchall()
        return requests
