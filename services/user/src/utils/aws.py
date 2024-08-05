import boto3
from datetime import datetime, timezone, timedelta
import json
from botocore.exceptions import ClientError

global_session_info = {'session': None, 'expiry': None}
session_duration = 1200  # How many seconds a session is valid for


def get_session():
    global global_session_info

    # Check if at least 5 minutes remain before the session expires
    future_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    if global_session_info['session'] and future_time < global_session_info['expiry']:
        return global_session_info['session']

    session = boto3.Session()

def get_session():
    # return boto3.Session()
    global global_session_info

    # Check if at least 5 minutes remain before the session expires
    future_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    if global_session_info['session'] and future_time < global_session_info['expiry']:
        return global_session_info['session']

    session = boto3.Session()

    expiry_time = datetime.now(timezone.utc) + \
        timedelta(seconds=session_duration)


def get_aws_secret(secret_name):
    # Create a Secrets Manager client
    session = get_session()
    if session is None:
        raise Exception("Failed to assume role and create session")

    client = session.client(
        service_name='secretsmanager', region_name='us-east-2')

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
        return json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None
