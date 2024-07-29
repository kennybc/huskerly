import json
from botocore.exceptions import ClientError
from role import assume_role


def get_aws_secret(secret_name):
    # Create a Secrets Manager client
    session = assume_role()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        raise e
    else:
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
