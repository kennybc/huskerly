import boto3
import json

from db.secrets import get_secrets


class MessageHandler:
    def __init__(self):
        # Connect to backend websocket endpoint
        secrets = get_secrets()
        self.client = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=secrets["ws_ep"],
            region_name="us-east-2",
        )

        #list of channel connections
        self.active_channel_conns = {
            "s_1" : [],
            "s_2" : []
        }

        # map of users to their active channel
        self.user_to_channel = dict()


    # lets a user join a channel to chat in
    def join_channel(self, channel_id, user_id):
        self.active_channel_conns[channel_id].append(user_id)
        self.user_to_channel[user_id] = channel_id

        
        print(self.active_channel_conns)
        print(self.user_to_channel)
        
        print(user_id + " has joined " + channel_id)
        self.send_to_channel(user_id, user_id + " has joined " + channel_id)

    #removes a user from their channels when they disconnect
    def leave_channels(self, user_id):
        #removes user from active channel listeners
        user_channel = self.user_to_channel[user_id]
        self.active_channel_conns[user_channel].remove(user_id)
        #removes their channel from them
        self.user_to_channel[user_id] = ""

        print("Diconnect user " + user_id)
        print(self.user_to_channel)
        print(self.active_channel_conns)
        

    # sends a message to everyone in a channel
    def send_to_channel(self, user_id, message):
        channel = self.user_to_channel[user_id]
        # if a user is disconnected / not in a channel atm
        if channel == "":
            return
        
        for recipient in self.active_channel_conns[channel]:
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
