import grpc
from concurrent import futures
import sys
sys.path.append('../protos')

import client_listener_pb2 as pb2
import client_listener_pb2_grpc as pb2_grpc
import server_pb2 as server_pb2

class Client_Listener(pb2_grpc.Client_ListenerServicer):
    '''
        Server ran by the client that listens for messages from the server
        that must be delivered immediately
    '''

    def __init__(self, update_ui_callback):
        self.update_ui_callback = update_ui_callback

    def SendOnlineMessage(self, request, context):
        sender = request.sender
        message = request.message

        display_text = f"\nNew message from {sender}: {message}"
        self.update_ui_callback(display_text)

        res = server_pb2.StandardServerResponse(success=True, message="Message received successfully")
        return res
    
