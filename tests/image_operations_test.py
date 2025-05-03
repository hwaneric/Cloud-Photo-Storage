import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import io
import grpc
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos')))
from client import Client
import server_pb2
import server_pb2_grpc

def test_upload_image_large_file():
    """Test uploading a large image file that requires multiple chunks"""
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        # Create a large image (2MB)
        img = Image.new('RGB', (1000, 1000), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        with patch("os.path.exists", return_value=True), \
             patch("os.path.getsize", return_value=len(img_byte_arr)), \
             patch("builtins.open", mock_open(read_data=img_byte_arr)), \
             patch.object(client.stub, 'UploadImage') as mock_upload:
            mock_upload.return_value = server_pb2.StandardServerResponse(
                success=True, 
                message="Image uploaded successfully."
            )
            success, message = client.upload_image("/tmp/large.jpg", "album1")
            assert success is True
            assert message == "Image uploaded successfully."
            # Verify that the image was sent in chunks
            assert mock_upload.call_count == 1

def test_fetch_photos_pagination():
    """Test fetching photos with pagination"""
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        # Create test chunks for two images
        chunks = []
        for i in range(2):
            # Metadata chunk
            metadata = server_pb2.ImageChunk()
            metadata.metadata.username = "testuser"
            metadata.metadata.album = "album1"
            metadata.metadata.image_name = f"img{i}.jpg"
            metadata.metadata.size = 123
            metadata.metadata.file_type = "jpg"
            chunks.append(metadata)
            
            # Data chunk
            data = server_pb2.ImageChunk()
            data.image_data = b"image_data"
            chunks.append(data)

        with patch.object(client.stub, 'FetchPhotos', return_value=iter(chunks)):
            success, images = client.fetch_photos("album1", page=0, page_size=2)
            assert success is True
            assert len(images) == 2
            assert images[0]["metadata"]["image_name"] == "img0.jpg"
            assert images[1]["metadata"]["image_name"] == "img1.jpg"

def test_fetch_photos_empty_album():
    """Test fetching photos from an empty album"""
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'FetchPhotos', return_value=iter([])):
            success, images = client.fetch_photos("empty_album", page=0, page_size=10)
            assert success is True
            assert len(images) == 0

def test_delete_image_not_owner():
    """Test deleting an image when user is not the owner"""
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'DeleteImage') as mock_delete:
            mock_delete.return_value = server_pb2.StandardServerResponse(
                success=False,
                message="You do not have permission to delete this image."
            )
            success, message = client.delete_image("album1", "img1.jpg")
            assert not success
            assert "permission" in message.lower()

def test_upload_image_invalid_path():
    """Test uploading an image with an invalid file path"""
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch("os.path.exists", return_value=False):
            success, message = client.upload_image("/nonexistent/path/image.jpg", "album1")
            assert not success
            assert "file" in message.lower()

def test_fetch_photos_invalid_album():
    """Test fetching photos from a non-existent album"""
    with patch.object(Client, '_update_leader', return_value=None):
        client = Client("127.0.0.1", 12345, "127.0.0.1")
        client.username = "testuser"
        client.stub = MagicMock()
        client.leader = 0
        client.stubs = {0: client.stub}

        with patch.object(client.stub, 'FetchPhotos') as mock_fetch:
            mock_fetch.side_effect = grpc.RpcError("Album not found")
            with pytest.raises(grpc.RpcError):
                client.fetch_photos("nonexistent_album", page=0, page_size=10) 