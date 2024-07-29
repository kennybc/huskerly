import boto3
# from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta
# load_dotenv()
import json
from botocore.exceptions import ClientError

global_session_info = {'session': None, 'expiry': None}
session_duration = 1200  # How many seconds a session is valid for


def assume_role():
    global global_session_info

    # Check if at least 5 minutes remain before the session expires
    if global_session_info['session'] and datetime.now(timezone.utc) + timedelta(minutes=5) < global_session_info['expiry']:
        return global_session_info['session']

    # Otherwise: proceed to create a new session

    # Check if running locally by looking for specific environment variables
    # if False and os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
    #     # Running locally, use credentials from .env
    #     session = boto3.Session(
    #         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    #         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    #         # AWS_SESSION_TOKEN is not needed for permanent credentials
    #     )
    #     # Local session is permanent
    #     expiry = datetime.now(timezone.utc) + timedelta(days=365)
    # else:
    # Running in AWS, assume the user service role
    sts_client = boto3.client('sts', region_name='us-east-2')
    try:
        assumed_role = sts_client.assume_role(
            RoleArn="arn:aws:iam::058264409130:role/UserServiceRole",
            RoleSessionName="AssumedRoleSession1",
            DurationSeconds=session_duration
        )
        credentials = assumed_role['Credentials']
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )
        expiry = credentials['Expiration']
    except ClientError as e:
        print(f"Error assuming role: {e}")
        return None

    global_session_info['session'] = session
    global_session_info['expiry'] = expiry
    return session


def get_aws_secret(secret_name):
    # Create a Secrets Manager client
    session = assume_role()
    if session is None:
        raise Exception("Failed to assume role and create session")

    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
        return json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None
