import boto3
import json

from handler import MessageHandler


class ChannelHandler:
    
    def __init__(self, id):
        #initial stream setup
        self.activeConnections = []
        self.channel_id = id

        messageHandler = MessageHandler()

    def join_channel(self, id):
        self.activeConnections.append(id)
        print(id + " has joined " + self.channel_id)
