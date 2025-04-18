import pytest
import time
import sys
import os
import grpc
import threading
from concurrent import futures
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../server')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos')))
from client import Client
from driver import serve
import server_pb2
import server_pb2_grpc

class MockServerServicer(server_pb2_grpc.ServerServicer):
    def Signup(self, request, context):
        if request.username and request.password:
            return server_pb2.StandardServerResponse(success=True, message="Signup successful")
        else:
            return server_pb2.StandardServerResponse(success=False, message="Username and/or password cannot be empty.")

    def Login(self, request, context):
        if request.username == "testuser" and request.password == "testpass":
            success_response = server_pb2.UserLoginSuccess(success=True, message="Login successful.", unread_message_count=5)
            return server_pb2.UserLoginResponse(success=success_response)
        else:
            failure_response = server_pb2.StandardServerResponse(success=False, message="Incorrect username or password. Please try again.")
            return server_pb2.UserLoginResponse(failure=failure_response)
    
    def ListUsernames(self, request, context):
        usernames = ["user1", "user2", "user3"]
        success_response = server_pb2.ListUsernames(success=True, message="Accounts listed successfully.", matches=usernames)
        return server_pb2.ListUsernamesResponse(success=success_response)
    
    def SendMessage(self, request, context):
        if request.message and request.target_username: 
            return server_pb2.StandardServerResponse(success=True, message="Message sent successfully.")
        else: 
            return server_pb2.StandardServerResponse(success=False, message="Target user does not exist.")
        
    def Logout(self, request, context):
        if request.username == "testuser":
            return server_pb2.StandardServerResponse(success=True, message="Logout successful.")
        else:
            return server_pb2.StandardServerResponse(success=False, message="Username does not exist.")
        
    def ReadMessages(self, request, context):
        if request.username and request.num_messages > 0:
            messages = [
                server_pb2.UnreadMessage(sender="user1", message="Hello!", timestamp=int(time.time())),
                server_pb2.UnreadMessage(sender="user2", message="How are you?", timestamp=int(time.time())),
                ]
            success_response = server_pb2.ReadMessage(success=True, message="Messages read successfully.", messages=messages)
            return server_pb2.ReadMessageResponse(success=success_response)
        else:
            failure_response = server_pb2.StandardServerResponse(success=False, message="Target user does not exist.")
            return server_pb2.ReadMessageResponse(failure=failure_response)
        
    def DeleteAccount(self, request, context):
        if request.username == "testuser":
            return server_pb2.StandardServerResponse(success=True, message="Account deleted successfully.")
        else:
            return server_pb2.StandardServerResponse(success=False, message="Username does not exist.")
        
    def FetchSentMessages(self, request, context):
        if request.username:
            sent_messages =[
                server_pb2.SentMessages(target_username="user1", messages=[
                    server_pb2.UnreadMessage(message_id="1", message="Hello!", timestamp=int(time.time())),
                    server_pb2.UnreadMessage(message_id="2", message="How are you?", timestamp=int(time.time()))
                ])
            ]
            success_response = server_pb2.FetchedSentMessages(success=True, sent_messages=sent_messages)
            return server_pb2.FetchSentMessagesResponse(success=success_response)
        else:
            failure_response = server_pb2.StandardServerResponse(success=False, message="Username cannot be empty.")
            return server_pb2.FetchSentMessagesResponse(failure=failure_response)
        
    def DeleteMessage(self, request, context):
        if request.sender_username and request.message_id:
            return server_pb2.StandardServerResponse(success=True, message="Message deleted successfully.")
        else:
            return server_pb2.StandardServerResponse(success=False, message="Message ID not found.")

@pytest.fixture(scope="module")
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_ServerServicer_to_server(MockServerServicer(), server)
    port = server.add_insecure_port('[::]:0')
    server.start()
    yield server, port
    server.stop(0)

@pytest.fixture(scope="module")
def grpc_stub(grpc_server):
    server, port = grpc_server
    channel = grpc.insecure_channel(f'localhost:{port}')
    stub = server_pb2_grpc.ServerStub(channel)
    yield stub
    channel.close()

def test_signup_success(grpc_stub):
    request = server_pb2.UserAuthRequest(username="testuser", password="testpass")
    response = grpc_stub.Signup(request)
    assert response.success
    assert response.message == "Signup successful"

def test_signup_failure(grpc_stub):
    request = server_pb2.UserAuthRequest(username="", password="testpass")
    response = grpc_stub.Signup(request)
    assert not response.success
    assert response.message == "Username and/or password cannot be empty."

def test_login_success(grpc_stub):
    request = server_pb2.UserAuthRequest(username="testuser", password="testpass")
    response = grpc_stub.Login(request)
    assert response.success.success
    assert response.success.message == "Login successful."
    assert response.success.unread_message_count == 5

def test_login_failure(grpc_stub):
    request = server_pb2.UserAuthRequest(username="wronguser", password="wrongpass")
    response = grpc_stub.Login(request)
    assert not response.failure.success
    assert response.failure.message == "Incorrect username or password. Please try again."

def test_list_usernames(grpc_stub):
    request = server_pb2.ListUsernamesRequest(username_pattern="user")
    response = grpc_stub.ListUsernames(request)
    assert response.success.success
    assert response.success.message == "Accounts listed successfully."
    assert response.success.matches == ["user1", "user2", "user3"]

def test_send_message_success(grpc_stub):
    request = server_pb2.SendMessageRequest(sender_username="testuser", target_username="user1", timestamp=int(time.time()), message="Hello, user1!")
    response = grpc_stub.SendMessage(request)
    assert response.success
    assert response.message == "Message sent successfully."

def test_send_message_failure(grpc_stub):
    request = server_pb2.SendMessageRequest(sender_username="testuser", target_username="", timestamp=int(time.time()), message="Hello, user1!")
    response = grpc_stub.SendMessage(request)
    assert not response.success
    assert response.message == "Target user does not exist."

def test_logout_success(grpc_stub):
    request = server_pb2.UserAuthRequest(username="testuser")
    response = grpc_stub.Logout(request)
    assert response.success
    assert response.message == "Logout successful."

def test_logout_failure(grpc_stub):
    request = server_pb2.UserAuthRequest(username=None)
    response = grpc_stub.Logout(request)
    assert not response.success
    assert response.message == "Username does not exist."

def test_read_message_success(grpc_stub):
    request = server_pb2.ReadMessagesRequest(username="testuser", num_messages=2)
    response = grpc_stub.ReadMessages(request)
    assert response.success.success
    assert response.success.message == "Messages read successfully."
    assert response.success.messages[0].sender == "user1"
    assert response.success.messages[0].message == "Hello!"
    assert response.success.messages[1].sender == "user2"
    assert response.success.messages[1].message == "How are you?"

def test_read_message_failure(grpc_stub):
    request = server_pb2.ReadMessagesRequest(username=None, num_messages=3)
    response = grpc_stub.ReadMessages(request)
    assert not response.failure.success
    assert response.failure.message == "Target user does not exist."

def test_delete_account_success(grpc_stub):
    request = server_pb2.UserAuthRequest(username="testuser")
    response = grpc_stub.DeleteAccount(request)
    assert response.success
    assert response.message == "Account deleted successfully."

def test_delete_account_failure(grpc_stub):
    request = server_pb2.UserAuthRequest(username="nonexistentuser")
    response = grpc_stub.DeleteAccount(request)
    assert not response.success
    assert response.message == "Username does not exist."

def test_fetch_sent_messages_success(grpc_stub):
    request = server_pb2.FetchSentMessagesRequest(username="testuser")
    response = grpc_stub.FetchSentMessages(request)
    assert response.success.success
    assert response.success.sent_messages[0].target_username == "user1"
    assert response.success.sent_messages[0].messages[0].message == "Hello!"
    assert response.success.sent_messages[0].messages[1].message == "How are you?"
    
def test_fetch_sent_messages_failure(grpc_stub):
    request = server_pb2.FetchSentMessagesRequest(username="")
    response = grpc_stub.FetchSentMessages(request)
    assert not response.failure.success
    assert response.failure.message == "Username cannot be empty."

def test_delete_messages_success(grpc_stub):
    request = server_pb2.DeleteMessageRequest(sender_username="testuser", message_id="1")
    response = grpc_stub.DeleteMessage(request)
    assert response.success
    assert response.message == "Message deleted successfully."

def test_delete_messages_failure(grpc_stub):
    request = server_pb2.DeleteMessageRequest(sender_username="test_user", message_id="")
    response = grpc_stub.DeleteMessage(request)
    assert not response.success
    assert response.message == "Message ID not found."