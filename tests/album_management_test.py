import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos')))
from client import Client
import server_pb2
import server_pb2_grpc

def test_create_album_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'CreateAlbum') as mock_create:
            mock_create.return_value = server_pb2.StandardServerResponse(
                success=True, 
                message="Album 'vacation' created successfully."
            )
            success, message = client.create_album("vacation")
            
            assert success is True
            assert message == "Album 'vacation' created successfully."
            mock_create.assert_called_once_with(
                server_pb2.CreateAlbumRequest(
                    username="testuser",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_create_album_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'CreateAlbum') as mock_create:
            mock_create.return_value = server_pb2.StandardServerResponse(
                success=False,
                message="Album 'vacation' already exists."
            )
            success, message = client.create_album("vacation")
            
            assert success is False
            assert message == "Album 'vacation' already exists."
            mock_create.assert_called_once_with(
                server_pb2.CreateAlbumRequest(
                    username="testuser",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_delete_album_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'DeleteAlbum') as mock_delete:
            mock_delete.return_value = server_pb2.StandardServerResponse(
                success=True,
                message="Album 'vacation' deleted successfully."
            )
            success, message = client.delete_album("vacation")
            
            assert success is True
            assert message == "Album 'vacation' deleted successfully."
            mock_delete.assert_called_once_with(
                server_pb2.DeleteAlbumRequest(
                    username="testuser",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_delete_album_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'DeleteAlbum') as mock_delete:
            mock_delete.return_value = server_pb2.StandardServerResponse(
                success=False,
                message="Album 'vacation' does not exist."
            )
            success, message = client.delete_album("vacation")
            
            assert success is False
            assert message == "Album 'vacation' does not exist."
            mock_delete.assert_called_once_with(
                server_pb2.DeleteAlbumRequest(
                    username="testuser",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_add_album_editor_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'AddAlbumEditor') as mock_add:
            mock_add.return_value = server_pb2.StandardServerResponse(
                success=True,
                message="User 'friend' added as editor to album 'vacation'."
            )
            success, message = client.add_album_editor("vacation", "friend")
            
            assert success is True
            assert message == "User 'friend' added as editor to album 'vacation'."
            mock_add.assert_called_once_with(
                server_pb2.AddAlbumEditorRequest(
                    requestor_username="testuser",
                    editor_username="friend",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_add_album_editor_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'AddAlbumEditor') as mock_add:
            mock_add.return_value = server_pb2.StandardServerResponse(
                success=False,
                message="User 'friend' does not exist."
            )
            success, message = client.add_album_editor("vacation", "friend")
            
            assert success is False
            assert message == "User 'friend' does not exist."
            mock_add.assert_called_once_with(
                server_pb2.AddAlbumEditorRequest(
                    requestor_username="testuser",
                    editor_username="friend",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_remove_album_editor_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'RemoveAlbumEditor') as mock_remove:
            mock_remove.return_value = server_pb2.StandardServerResponse(
                success=True,
                message="User 'friend' removed as editor from album 'vacation'."
            )
            success, message = client.remove_album_editor("vacation", "friend")
            
            assert success is True
            assert message == "User 'friend' removed as editor from album 'vacation'."
            mock_remove.assert_called_once_with(
                server_pb2.RemoveAlbumEditorRequest(
                    requestor_username="testuser",
                    editor_username="friend",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_remove_album_editor_failure():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'RemoveAlbumEditor') as mock_remove:
            mock_remove.return_value = server_pb2.StandardServerResponse(
                success=False,
                message="User 'friend' is not an editor of album 'vacation'."
            )
            success, message = client.remove_album_editor("vacation", "friend")
            
            assert success is False
            assert message == "User 'friend' is not an editor of album 'vacation'."
            mock_remove.assert_called_once_with(
                server_pb2.RemoveAlbumEditorRequest(
                    requestor_username="testuser",
                    editor_username="friend",
                    album_name="vacation",
                    from_client=True
                )
            )

def test_get_album_editors_success():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.leader = 0
        
        # Mock the metadata file
        metadata_content = {
            "editors": ["testuser", "friend1", "friend2"]
        }
        
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=str(metadata_content))), \
             patch("json.load", return_value=metadata_content):
            editors = client.get_album_editors("vacation")
            assert editors == ["testuser", "friend1", "friend2"]

def test_get_album_editors_no_metadata():
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345)
        client.username = "testuser"
        client.leader = 0
        
        with patch("os.path.exists", return_value=False):
            editors = client.get_album_editors("vacation")
            assert editors == [] 