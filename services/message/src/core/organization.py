

from utils.aws import get_aws_secret, get_session
from utils.connect import get_cursor

pool_id = get_aws_secret("huskerly_userpool_id")["id"]


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

        session = get_session()
        client = session.client('cognito-idp', region_name='us-east-2')

        response = client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=creator_email,
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
                    'Value': 'MEMBER'
                }
            ]
        )

        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
            raise Exception(f"""Failed to update user {
                            creator_email} with organization {org_id} in Cognito.""")

        return org_id
