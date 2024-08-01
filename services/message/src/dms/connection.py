import boto3
import json



class ConnectionHandler:
    
    def __init__(self, id):
        # DynamoDB table to track connections
        self.table = boto3.resource(
            "dynamodb",
            region_name="us-east-2",
        ).Table("huskerly-ws-connections")

    #register an active connection
    def add_connection(self, id):
        self.table.put_item(Item={"connection_id": id})
        return

    # remove an active connection
    def remove_connection(self, id):
        self.table.delete_item(Key={"connection_id": id})
        return



   