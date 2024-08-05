import boto3
from datetime import datetime, timezone, timedelta
import json

global_session_info = {"session": None, "expiry": None}
session_duration = 1200  # How many seconds a session is valid for


def get_session():
    global global_session_info

    # Check if at least 5 minutes remain before the session expires
    future_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    if global_session_info["session"] and future_time < global_session_info["expiry"]:
        return global_session_info["session"]

    session = boto3.Session()

    expiry_time = datetime.now(timezone.utc) + \
        timedelta(seconds=session_duration)

    global_session_info["session"] = session
    global_session_info["expiry"] = expiry_time
    return session


def get_secrets():
    # Create a Secrets Manager client
    session = get_session()
    if session is None:
        raise Exception("Failed to create session")

    client = session.client(
        service_name="secretsmanager", region_name="us-east-2")

    get_secret_value_response = client.get_secret_value(
        SecretId="huskerly-secrets-user"
    )
    return json.loads(get_secret_value_response["SecretString"])
