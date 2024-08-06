import boto3
import json


def get_secrets():
    client = boto3.client(
        service_name="secretsmanager", region_name="us-east-2")

    get_secret_value_response = client.get_secret_value(
        SecretId="huskerly-secrets-message"
    )
    return json.loads(get_secret_value_response["SecretString"])