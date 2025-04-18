import pytest
from unittest.mock import patch, MagicMock, ANY
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos')))
from client import Client
import server_pb2
import server_pb2_grpc

def test_signup_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        with patch.object(client.stub, 'Signup') as mock_signup:
            mock_signup.return_value = server_pb2.StandardServerResponse(success=True, message="Successfully signed up!")
            success, message = client.signup("testuser", "password123")

            assert success == True
            assert message == "Successfully signed up!"
            assert client.username == "testuser"
            mock_signup.assert_called_once_with(server_pb2.UserAuthRequest(username="testuser", password="password123", from_client=True))

def test_signup_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        with patch.object(client.stub, 'Signup') as mock_signup:
            mock_signup.return_value = server_pb2.StandardServerResponse(success=False, message="Username already exists.")
            success, message = client.signup("testuser", "password123")
            
            assert success == False
            assert message == "Username already exists."
            assert client.username == None
            mock_signup.assert_called_once_with(server_pb2.UserAuthRequest(username="testuser", password="password123", from_client=True))

def test_login_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        response = server_pb2.UserLoginResponse()
        response.success.CopyFrom(server_pb2.UserLoginSuccess(success=True, message="Successfully logged in!", unread_message_count=5))

        with patch.object(client.stub, 'Login', return_value=response) as mock_login:
            success, message, unread_message_count = client.login("testuser", "password123")

            assert success == True
            assert message == "Successfully logged in!"
            assert unread_message_count == 5
            assert client.username == "testuser"
            mock_login.assert_called_once_with(server_pb2.UserAuthRequest(username="testuser", password="password123", from_client=True))

def test_login_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        response = server_pb2.UserLoginResponse()
        response.failure.CopyFrom(server_pb2.StandardServerResponse(success=False, message="Invalid credentials."))

        with patch.object(client.stub, 'Login', return_value=response) as mock_login:
            success, message, unread_message_count = client.login("testuser", "wrongpassword")

            assert success == False
            assert message == "Invalid credentials."
            assert unread_message_count == -1
            assert client.username == None
            mock_login.assert_called_once_with(server_pb2.UserAuthRequest(username="testuser", password="wrongpassword", from_client=True))

def test_list_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        response = server_pb2.ListUsernamesResponse()
        response.success.CopyFrom(server_pb2.ListUsernames(success=True, message="Accounts listed successfully.", matches=["user1", "user2"]))

        with patch.object(client.stub, 'ListUsernames', return_value=response) as mock_list:
            success, matches = client.list("user")
            assert success == True
            assert matches == ["user1", "user2"]
            assert client.username == "testuser"
            mock_list.assert_called_once_with(server_pb2.ListUsernamesRequest(username_pattern="user"))

def test_list_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        response = server_pb2.ListUsernamesResponse()
        response.failure.CopyFrom(server_pb2.StandardServerResponse(success=False, message="Invalid regex pattern."))
        with patch.object(client.stub, 'ListUsernames', return_value=response) as mock_list:
            success, message = client.list("?")

            assert success == False
            assert message == "Invalid regex pattern."
            assert client.username == "testuser"
            mock_list.assert_called_once_with(server_pb2.ListUsernamesRequest(username_pattern="?"))

def test_message_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        with patch.object(client.stub, 'SendMessage', return_value=server_pb2.StandardServerResponse(success=True, message="Message sent successfully.")) as mock_message:
            success, message = client.message("targetuser", "Hello")

            assert success == True
            assert message == "Message sent successfully."
            assert client.username == "testuser"

            actual_call_args = mock_message.call_args[0][0]

            assert actual_call_args.sender_username == "testuser"
            assert actual_call_args.target_username == "targetuser"
            assert actual_call_args.message == "Hello"
            current_time = int(time.time())
            assert current_time - actual_call_args.timestamp <= 5

def test_message_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        with patch.object(client.stub, 'SendMessage', return_value=server_pb2.StandardServerResponse(success=False, message="Target user does not exist.")) as mock_message:
            success, message = client.message("nonexistentuser", "Hello")

            assert success == False
            assert message == "Target user does not exist."
            assert client.username == "testuser"

            actual_call_args = mock_message.call_args[0][0]

            assert actual_call_args.sender_username == "testuser"
            assert actual_call_args.target_username == "nonexistentuser"
            assert actual_call_args.message == "Hello"
            current_time = int(time.time())
            assert current_time - actual_call_args.timestamp <= 5

def test_logout_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        with patch.object(client.stub, 'Logout', return_value=server_pb2.StandardServerResponse(success=True, message="Logout Successful.")) as mock_logout:
            success, message = client.logout()

            assert success == True
            assert message == "Logout Successful."
            assert client.username == None
            mock_logout.assert_called_once_with(server_pb2.UserLogoutRequest(username="testuser", from_client=True))

def test_logout_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        with patch.object(client.stub, 'Logout', return_value=server_pb2.StandardServerResponse(success=False, message="Logout failed.")) as mock_logout:
            success, message = client.logout()

            assert success == False
            assert message == "Logout failed."
            assert client.username == "testuser"
            mock_logout.assert_called_once_with(server_pb2.UserLogoutRequest(username="testuser", from_client=True))

def test_read_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        response = server_pb2.ReadMessageResponse()
        response.success.success = True
        response.success.message = "Messages found."
        message = response.success.messages.add()
        message.sender = "user1"
        message.timestamp = 1617184800
        message.message = "Hello!"
        
        with patch.object(client.stub, 'ReadMessages') as mock_read_messages:
            mock_read_messages.return_value = response
            
            success, messages = client.read(1)
            
            assert success == True
            assert messages == ["user1 at (03-31-2021, 06:00 AM): Hello!"]
            mock_read_messages.assert_called_once_with(server_pb2.ReadMessagesRequest(username="testuser", num_messages=1, from_client=True))

def test_read_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        response = server_pb2.ReadMessageResponse()
        response.failure.success = False
        response.failure.message = "No messages found."
        
        with patch.object(client.stub, 'ReadMessages') as mock_read_messages:
            mock_read_messages.return_value = response
            
            success, message = client.read(1)
            
            assert success == False
            assert message == "No messages found."
            mock_read_messages.assert_called_once_with(server_pb2.ReadMessagesRequest(username="testuser", num_messages=1, from_client=True))

def test_delete_account_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        with patch.object(client.stub, 'DeleteAccount') as mock_delete_account:
            mock_delete_account.return_value = server_pb2.StandardServerResponse(success=True, message="Successfully deleted account!")
            
            success, message = client.delete_account()
            
            assert success == True
            assert message == "Successfully deleted account!"
            assert client.username == None
            mock_delete_account.assert_called_once_with(server_pb2.DeleteAccountRequest(username="testuser", from_client=True))

def test_delete_account_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        with patch.object(client.stub, 'DeleteAccount') as mock_delete_account:
            mock_delete_account.return_value = server_pb2.StandardServerResponse(success=False, message="Delete account failed.")
        
            success, message = client.delete_account()
        
            assert success == False
            assert message == "Delete account failed."
            assert client.username == "testuser"
            mock_delete_account.assert_called_once_with(server_pb2.DeleteAccountRequest(username="testuser", from_client=True))

def test_fetch_sent_messages_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        response = server_pb2.FetchSentMessagesResponse()
        response.success.success = True
        response.success.message = "Sent messages fetched successfully."
        sent_message_1 = server_pb2.SentMessages(target_username="user1")
        sent_message_1.messages.add(sender="testuser", timestamp=1617184800, message="Message 1")
        sent_message_2 = server_pb2.SentMessages(target_username="user2")
        sent_message_2.messages.add(sender="testuser", timestamp=1617184801, message="Message 2")
        response.success.sent_messages.extend([sent_message_1, sent_message_2])
        
        with patch.object(client.stub, 'FetchSentMessages') as mock_fetch_sent_messages:
            mock_fetch_sent_messages.return_value = response
            
            success, sent_messages = client.fetch_sent_messages()
            
            assert success == True
            expected_messages = {
                "user1": [{"message": "Message 1", "message_id": '', "timestamp": 1617184800}],
                "user2": [{"message": "Message 2", "message_id": '', "timestamp": 1617184801}]
            }
            assert sent_messages == expected_messages
            mock_fetch_sent_messages.assert_called_once_with(server_pb2.FetchSentMessagesRequest(username="testuser"))

def test_fetch_sent_messages_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute

        response = server_pb2.FetchSentMessagesResponse()
        response.failure.success = False
        response.failure.message = "No sent messages found."

        with patch.object(client.stub, 'FetchSentMessages') as mock_fetch_sent_messages:
            mock_fetch_sent_messages.return_value = response
            success, message = client.fetch_sent_messages()
            assert success == False
            assert message == "No sent messages found."
            mock_fetch_sent_messages.assert_called_once_with(server_pb2.FetchSentMessagesRequest(username="testuser"))

def test_delete_message_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        with patch.object(client.stub, 'DeleteMessage') as mock_delete_message:
            mock_delete_message.return_value = server_pb2.StandardServerResponse(success=True, message="Message deleted successfully.")
            
            success, message = client.delete_message("1")
            
            assert success == True
            assert message == "Message deleted successfully."
            mock_delete_message.assert_called_once_with(server_pb2.DeleteMessageRequest(sender_username="testuser", message_id="1", from_client=True))

def test_delete_message_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0  # Mock the leader attribute
        client.stubs = {0: client.stub}  # Mock the stubs attribute
        
        with patch.object(client.stub, 'DeleteMessage') as mock_delete_message:
            mock_delete_message.return_value = server_pb2.StandardServerResponse(success=False, message="Delete message failed.")

            success, message = client.delete_message("1")

            assert success == False
            assert message == "Delete message failed."
            mock_delete_message.assert_called_once_with(server_pb2.DeleteMessageRequest(sender_username="testuser", message_id="1", from_client=True))