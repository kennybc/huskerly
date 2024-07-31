import boto3
import json

from db.secrets import get_secrets


class DMHandler:
    def __init__(self):
        # Connect to backend websocket endpoint
        secrets = get_secrets()
        self.client = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=secrets["ws_ep"],
            region_name="us-east-2",
        )

        # DynamoDB table to track connections
        self.table = boto3.resource(
            "dynamodb",
            region_name="us-east-2",
        ).Table("huskerly-ws-connections")

    def add_connection(self, id):
        self.table.put_item(Item={"connection_id": id})

    def remove_connection(self, id):
        # self.table.delete_item(Key={"connection_id": id})
        return

    def send_dm(self, recipient, message):
        try:
            response = self.client.post_to_connection(
                ConnectionId=recipient, Data=json.dumps(message).encode("utf-8")
            )
            print(f"Message sent to connection ID {recipient}, Response: {response}")

        except self.client.exceptions.GoneException:
            print(f"Connection ID {recipient} is no longer available.")

        except Exception as e:
            print(f"Error sending message: {e}")

    def broadcast(self, message):
        recipients = self.table.scan()["Items"]
        for recipient in recipients:
            self.send_dm(recipient["connection_id"], message)
