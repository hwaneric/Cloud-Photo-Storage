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
    
    def Logout(self, request, context):
        if request.username == "testuser":
            return server_pb2.StandardServerResponse(success=True, message="Logout successful.")
        else:
            return server_pb2.StandardServerResponse(success=False, message="Username does not exist.")
        
    def DeleteAccount(self, request, context):
        if request.username == "testuser":
            return server_pb2.StandardServerResponse(success=True, message="Account deleted successfully.")
        else:
            return server_pb2.StandardServerResponse(success=False, message="Username does not exist.")
        
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