import boto3
import json

from utils.secrets import get_secrets
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ValidationError


# Connect to backend websocket endpoint
secrets = get_secrets()
client = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url=secrets["ws_ep"],
    region_name="us-east-2",
)

# channels containing their users
active_channel_conns = boto3.resource(
    "dynamodb",
    region_name="us-east-2",
).Table("huskerly-ws-channels")

# DynamoDB table to track connections + their channels
connections = boto3.resource(
    "dynamodb",
    region_name="us-east-2",
).Table("huskerly-ws-connections")

    # register an active connection
def add_connection(id):
    connections.put_item(Item={"connection_id": id})
    return

# remove an active connection
def remove_connection(id):
    # get the user's channel to remove them from
    response = connections.get_item(Key={"connection_id": id})
    channel = response["Item"].get("channel", [])

    leave_channel(id, channel) 
    connections.delete_item(Key={"connection_id": id})
    return
    
# creates a channel to be chatted in
def create_channel(channel_id):
    active_channel_conns.put_item(Item={"channel_id" : channel_id,
                                        "active_connections" : []})


# lets a user join a channel to chat in
def join_channel(channel_id, user_email, connection_id):
    # Attempts to add channel to user connection, if it already exists its updated
    print("Attempted join_channel")
    try:
        response = connections.put_item(
            Item={"connection_id": connection_id, "channel": channel_id, "email" : user_email},
            ConditionExpression=Attr("userid").ne(connection_id),
        )

        print("Added user to connection db:")
    except Exception as ce:
        if ce.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print("Key already exists")
            response = connections.update_item(
                Key={"userid": connection_id},
                UpdateExpression="set channel = :channel_id",
                ExpressionAttributeValues={":channel_id": channel_id},
            )
            response2 = connections.update_item(
                Key={"userid": connection_id},
                UpdateExpression="set email = :user_email",
                ExpressionAttributeValues={":user_email": user_email},
            )
            print("Update existing item succeeded:")
        else:
            print("Unexpected error: %s" % ce)

    # attepts to add user to channel connection list
    response = active_channel_conns.update_item(
        Key={"channel_id": channel_id},
        UpdateExpression="SET active_connections = list_append(active_connections, :i)",
        ExpressionAttributeValues={":i": [connection_id]},
        ReturnValues="UPDATED_NEW",
    )

    # if that worked
    print(user_email + " has joined " + channel_id)
        

# removes a user from their channels when they disconnect
def leave_channel(user_id, channel_id):
    print("attempting leave channel")
    # removes user from active channel listeners
    response = active_channel_conns.get_item(Key={"channel_id": channel_id})
    try:
        active_connections = response["Item"].get("active_connections", [])

        # removes user if they're there
        if user_id in active_connections:
            active_connections.remove(user_id)
        else:
            print(f"{user_id} not found in active_connections")

        # updates db
        response = active_channel_conns.update_item(
            Key={"channel_id": channel_id},
            UpdateExpression="SET active_connections = :new_list",
            ExpressionAttributeValues={":new_list": active_connections},
            ReturnValues="UPDATED_NEW",
        )
    except ValidationError:
        # If we're here, the user doesn't have a team, so no need to do any removal
        pass
            

# sends a message to everyone in a channel
def send_to_channel(user_id, message):
    print("send_to_channel")

    # get the channel the user is actively in
    response = connections.get_item(Key={"connection_id": user_id})

    channel = response["Item"].get("channel", [])
    email = response["Item"].get("email", [])
    print("Got channel " + channel + " for email " + email)

    # get the active users in the channel
    response = active_channel_conns.get_item(Key={"channel_id": channel})
    users = response["Item"].get("active_connections", [])

    print("alleged channel: " + channel)
    print("alledeg users: ")
    print(users)

    # NEED TO CONTINUE HERE
    for recipient in users:
        send_message(recipient, [email, message])

# message inclues the sender's id and their message
def send_message(recipient, message):
    try:
        response = client.post_to_connection(
            ConnectionId=recipient, Data=json.dumps(message).encode("utf-8")
        )
        print(f"Message sent to connection ID {recipient}")

    except client.exceptions.GoneException:
        print(f"Connection ID {recipient} is no longer available.")

    except Exception as e:
        print(f"Error sending message: {e}")

# deprecated but don't want to delete
# def broadcast(message):
#     recipients = table.scan()["Items"]
#     for recipient in recipients:
#         print("Sending to: " + recipient["connection_id"])
#         send_message(recipient["connection_id"], message)
