import boto3
import json

from db.secrets import get_secrets
from boto3.dynamodb.conditions import Attr
import botocore.exceptions

class MessageHandler:
    def __init__(self):
        # Connect to backend websocket endpoint
        secrets = get_secrets()
        self.client = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=secrets["ws_ep"],
            region_name="us-east-2",
        )

        # channels containing their users
        self.active_channel_conns = boto3.resource(
            "dynamodb",
            region_name="us-east-2",
        ).Table("huskerly-ws-channels")
        
        # DynamoDB table to track connections + their channels
        self.connections = boto3.resource(
            "dynamodb",
            region_name="us-east-2",
        ).Table("huskerly-ws-connections")

    #register an active connection
    def add_connection(self, id):
        self.connections.put_item(Item={"connection_id": id})
        return

    # remove an active connection
    def remove_connection(self, id):
        # get the user's channel to remove them from 
        response = self.connections.get_item(
            Key={
                'connection_id': id
            }
        )
        channel = response["Item"].get('channel', [])
        
        self.leave_channel(id, channel)
        self.connections.delete_item(Key={"connection_id": id})
        return

    # lets a user join a channel to chat in
    def join_channel(self, channel_id, user_id):
        #Attempts to add channel to user connection, if it already exists its updated
        print("Attempted join_channel")
        try :
            response = self.connections.put_item(
            Item={
                    'connection_id': user_id,
                    'channel' : channel_id        
                },
                ConditionExpression=Attr('userid').ne(user_id)        
            )

            print("Added user to connection db:")
        except Exception as ce :    
            if ce.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print("Key already exists")
                response = self.connections.update_item(
                    Key={'userid': user_id},
                    UpdateExpression="set channel = :channel_id",
                    ExpressionAttributeValues={":channel_id" : channel_id }
                )
                print("Update existing item succeeded:")
            else:
                print("Unexpected error: %s" % ce)
                


        # attepts to add user to channel connection list
        response = self.active_channel_conns.update_item(
            Key={
                'channel_id': channel_id
            },
            UpdateExpression="SET active_connections = list_append(active_connections, :i)",
            ExpressionAttributeValues={
                ':i': [user_id]
            },
            ReturnValues="UPDATED_NEW"
        )

        # if that worked
        print(user_id + " has joined " + channel_id)
        self.send_to_channel(user_id, user_id + " has joined " + channel_id)

    #removes a user from their channels when they disconnect
    def leave_channel(self, user_id, channel_id):
        #removes user from active channel listeners
        
        response = self.active_channel_conns.get_item(Key={'channel_id': channel_id})
        try:
            active_connections = response["Item"].get("active_connections", [])
        
             # removes user if they're there
            if user_id in active_connections:
                active_connections.remove(user_id)
            else:
                print(f"{user_id} not found in active_connections")

            # updates db
            response = self.active_channel_conns.update_item(
                Key={
                    'channel_id': channel_id
                },
                UpdateExpression="SET active_connections = :new_list",
                ExpressionAttributeValues={
                    ':new_list': active_connections
                },
                ReturnValues="UPDATED_NEW"
            )
        except ValidationException:
            #If we're here, the user doesn't have a team, so no need to do any removal
       
        

    # sends a message to everyone in a channel
    def send_to_channel(self, user_id, message):
        print("send_to_channel")

        # get the channel the user is actively in
        response = self.connections.get_item(
            Key={
                'connection_id': user_id
            }
        )
        
        channel = response['Item'].get('channel', [])
        print("Got channel " + channel)


        # get the active users in the channel
        response = self.active_channel_conns.get_item(
            Key={
                'channel_id': channel
            }
        )
        users = response['Item'].get('active_connections', [])

        print("alleged channel: " + channel)
        print("alledeg users: ")
        print(users)


        # NEED TO CONTINUE HERE
        for recipient in users:
            self.send_message(recipient, message)


    def send_message(self, recipient, message):
        try:
            response = self.client.post_to_connection(
                ConnectionId=recipient, Data=json.dumps(message).encode("utf-8")
            )
            print(f"Message sent to connection ID {recipient}")

        except self.client.exceptions.GoneException:
            print(f"Connection ID {recipient} is no longer available.")

        except Exception as e:
            print(f"Error sending message: {e}")


    # depricated but don't want to delete
    def broadcast(self, message):
        recipients = self.table.scan()["Items"]
        for recipient in recipients:
            print("Sending to: " + recipient["connection_id"])
            self.send_message(recipient["connection_id"], message)
