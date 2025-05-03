import pytest
from unittest.mock import patch, MagicMock, ANY, mock_open
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
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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

def test_logout_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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

def test_delete_account_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
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
        client = Client("127.0.0.1", 12345)
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

def test_upload_image_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}
        with patch("os.path.exists", return_value=True), \
             patch("os.path.getsize", return_value=123), \
             patch("builtins.open", mock_open(read_data=b"data")), \
             patch.object(client.stub, 'UploadImage') as mock_upload:
            mock_upload.return_value = server_pb2.StandardServerResponse(success=True, message="Image uploaded successfully.")
            success, message = client.upload_image("/tmp/test.jpg", "album1")
            assert success is True
            assert message == "Image uploaded successfully."

def test_upload_image_unsupported_filetype():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}
        with patch("os.path.exists", return_value=True), \
             patch("os.path.getsize", return_value=123), \
             patch("builtins.open", mock_open(read_data=b"data")):
            success, message = client.upload_image("/tmp/test.txt", "album1")
            assert success is None or success is False
            assert "Unsupported file type" in str(message)

def test_upload_image_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}
        with patch("os.path.exists", return_value=True), \
             patch("os.path.getsize", return_value=123), \
             patch("builtins.open", mock_open(read_data=b"data")), \
             patch.object(client.stub, 'UploadImage') as mock_upload:
            mock_upload.return_value = server_pb2.StandardServerResponse(success=False, message="Album does not exist")
            success, message = client.upload_image("/tmp/test.jpg", "album1")
            assert not success
            assert "Album does not exist" in message

def test_fetch_photos_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}
        # Simulate a stream of two images
        chunk1 = server_pb2.ImageChunk()
        chunk1.metadata.username = "testuser"
        chunk1.metadata.album = "album1"
        chunk1.metadata.image_name = "img1.jpg"
        chunk1.metadata.size = 123
        chunk1.metadata.file_type = "jpg"
        chunk2 = server_pb2.ImageChunk()
        chunk2.image_data = b"data"
        with patch.object(client.stub, 'FetchPhotos', return_value=iter([chunk1, chunk2])) as mock_fetch:
            success, images = client.fetch_photos("album1", 0, 10)
            assert success is True
            assert len(images) == 1
            assert images[0]["metadata"]["image_name"] == "img1.jpg"
            assert isinstance(images[0]["data"], bytearray)

def test_delete_image_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}
        with patch.object(client.stub, 'DeleteImage') as mock_delete:
            mock_delete.return_value = server_pb2.StandardServerResponse(success=True, message="Image deleted successfully.")
            success, message = client.delete_image("album1", "img1.jpg")
            assert success is True
            assert message == "Image deleted successfully."

def test_delete_image_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}
        with patch.object(client.stub, 'DeleteImage') as mock_delete:
            mock_delete.return_value = server_pb2.StandardServerResponse(success=False, message="Image does not exist.")
            success, message = client.delete_image("album1", "img1.jpg")
            assert not success
            assert message == "Image does not exist."
