import boto3
import json

from db.secrets import get_secrets

class DMHandler:
  def __init__(self):
    # Connect to backend websocket endpoint
    secrets = get_secrets()
    self.client = boto3.client("apigatewaymanagementapi", endpoint_url=secrets["ws_ep"])

    # Connect to DynamoDB table to log connections
    dynamodb = boto3.resource("dynamodb")
    self.table = dynamodb.Table("huskerly-ws-connections")

  #def add_connection():
    #self.table.

  def send_dm(self, recipient, message):
    try:
      response = self.client.post_to_connection(
          ConnectionId=recipient,
          Data=json.dumps(message).encode('utf-8')
      )
      print(f"Message sent to connection ID {recipient}, Response: {response}")

    except self.client.exceptions.GoneException:
      print(f"Connection ID {recipient} is no longer available.")

    except Exception as e:
      print(f"Error sending message: {e}")