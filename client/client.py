from collections import defaultdict
import functools
import datetime
import time
from dotenv import load_dotenv
import readline # Need to import readline to allow inputs to accept string with length > 1048
import sys
import grpc
from concurrent import futures
from decorators import retry_on_failure
sys.path.append('../protos')
import server_pb2
import server_pb2_grpc
import client_listener_pb2
import client_listener_pb2_grpc

from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)

class Client:
    def __init__(self, server_host, server_port, client_host, username=None):
        self.server_host = server_host
        self.server_port = server_port
        self.client_host = client_host

        self.username = username

        self.stubs = {} # Maps server_id to the corresponding stub for that server

        for server_id in range(3):
            host = os.getenv(f"SERVER_HOST_{server_id}")
            port = int(os.getenv(f"SERVER_PORT_{server_id}"))

            channel = grpc.insecure_channel(f"{host}:{port}")
            stub = server_pb2_grpc.ServerStub(channel)

            self.stubs[server_id] = stub

        self.leader = None
        self._update_leader()   # Initializes leader to the current leader server
    
    @retry_on_failure()
    def signup(self, username, password):
        ''' 
            Attempts to create a new account with the given username and password. 
        '''

        request = {
            "username": username, 
            "password": password,
            "from_client": True,
        }

        request = server_pb2.UserAuthRequest(**request)
        res = self.stubs[self.leader].Signup(request)

        if res.success:
            self.username = username

        return res.success, res.message
    
    @retry_on_failure()
    def login(self, username, password):
        '''
            Attempts to login with the given username and password.
        '''

        request = {
            "username": username, 
            "password": password,
            "from_client": True,
        }

        request = server_pb2.UserAuthRequest(**request)
        response = self.stubs[self.leader].Login(request)

        if response.HasField("success"):
            res = response.success
            self.username = username
            return res.success, res.message, res.unread_message_count
        else:
            res = response.failure
            return res.success, res.message, -1
   
    @retry_on_failure()
    def list(self, username_pattern):
        '''
            Lists all usernames that match the given regex username pattern.
        '''

        request = {
            "username_pattern": username_pattern
        }
        request = server_pb2.ListUsernamesRequest(**request)
        response = self.stubs[self.leader].ListUsernames(request)

        if response.HasField("success"):
            res = response.success
            return res.success, res.matches
        else:
            res = response.failure
            return res.success, res.message
    
    @retry_on_failure()
    def logout(self):
        '''
            Logs out the current user.
        '''

        request = {
            "username": self.username,
            "from_client": True,
        }
        request = server_pb2.UserLogoutRequest(**request)
        res = self.stubs[self.leader].Logout(request)

        if res.success:
            self.username = None
            return res.success, res.message
        else:
            return res.success, res.message
        
    @retry_on_failure()
    def delete_account(self):
        '''
            Deletes the current user's account.
        '''

        request = {
            "username": self.username,
            "from_client": True,
        }

        request = server_pb2.DeleteAccountRequest(**request)
        res = self.stubs[self.leader].DeleteAccount(request)

        if res.success:
            self.username = None
            return res.success, res.message
        else:
            return res.success, res.message

    def _update_leader(self):
        # Ask servers 0 and 1 who the current leader is
        leader = None

        for server_id in range(3):
            try:
                stub = self.stubs[server_id]
                request = server_pb2.CurrentLeaderRequest()
                response = stub.CurrentLeader(request)
                
                if not leader:
                    leader = response.leader
                elif response.leader != leader:
                    print(f"Server {server_id} has a different leader than server {self.leader}.")
                    raise Exception("Inconsistent leader information from servers.")
                    

            except grpc.RpcError as e:
                print(f"Error connecting to server {server_id}, server {server_id} is likely dead")
    
        if leader is None:
            print("Could not determine the current leader. Panicking.")
            raise Exception("Could not determine the current leader")
        
        self.leader = leader
        print(f"Current leader is server {self.leader}")

    @retry_on_failure()
    def create_album(self, album_name):
        '''
            Creates a new album for the current user.
        '''
        request = {
            "username": self.username,
            "album_name": album_name,
            "from_client": True,
        }
        request = server_pb2.CreateAlbumRequest(**request)
        res = self.stubs[self.leader].CreateAlbum(request)
        return res.success, res.message

    @retry_on_failure()
    def delete_album(self, album_name):
        '''
            Deletes an album for the current user.
        '''
        request = {
            "username": self.username,
            "album_name": album_name,
            "from_client": True,
        }
        request = server_pb2.DeleteAlbumRequest(**request)
        res = self.stubs[self.leader].DeleteAlbum(request)
        return res.success, res.message

    @retry_on_failure()
    def add_album_editor(self, album_name, editor_username):
        '''
            Adds an editor to an album.
        '''
        request = {
            "requestor_username": self.username,
            "editor_username": editor_username,
            "album_name": album_name,
            "from_client": True,
        }
        request = server_pb2.AddAlbumEditorRequest(**request)
        res = self.stubs[self.leader].AddAlbumEditor(request)
        return res.success, res.message

    @retry_on_failure()
    def remove_album_editor(self, album_name, editor_username):
        '''
            Removes an editor from an album.
        '''
        request = {
            "requestor_username": self.username,
            "editor_username": editor_username,
            "album_name": album_name,
            "from_client": True,
        }
        request = server_pb2.RemoveAlbumEditorRequest(**request)
        res = self.stubs[self.leader].RemoveAlbumEditor(request)
        return res.success, res.message

    @retry_on_failure()
    def upload_image(self, image_path, album_name):
        '''
            Uploads an image to an album.
        '''
        if not os.path.exists(image_path):
            return False, "File does not exist."

        image_name = os.path.basename(image_path)
        file_type = image_name.split('.')[-1].lower()
        if file_type not in ['jpg', 'jpeg', 'png']:
            return False, "Unsupported file type. Supported types are: jpg, jpeg, png"

        def generate_image_chunks():
            metadata = server_pb2.ImageMetadata(
                username=self.username,
                album=album_name,
                image_name=image_name,
                size=os.path.getsize(image_path),
                file_type=file_type
            )
            yield server_pb2.ImageChunk(metadata=metadata, from_client=True)

            # Then send image data in chunks
            with open(image_path, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    yield server_pb2.ImageChunk(image_data=chunk, from_client=True)

        try:
            res = self.stubs[self.leader].UploadImage(generate_image_chunks())
            return res.success, res.message
        except Exception as e:
            return False, str(e)

    @retry_on_failure()
    def delete_image(self, album_name, image_name):
        '''
            Deletes an image from an album.
        '''
        request = {
            "username": self.username,
            "album_name": album_name,
            "image_name": image_name,
            "from_client": True,
        }
        request = server_pb2.DeleteImageRequest(**request)
        res = self.stubs[self.leader].DeleteImage(request)
        return res.success, res.message

    @retry_on_failure()
    def fetch_photos(self, album_name, page=0, page_size=10):
        '''
            Fetches photos from an album with pagination.
        '''
        request = {
            "username": self.username,
            "album_name": album_name,
            "page": page,
            "page_size": page_size,
            "from_client": True,
        }
        request = server_pb2.FetchPhotosRequest(**request)
        response = self.stubs[self.leader].FetchPhotos(request)
        
        images = []
        for chunk in response:
            if chunk.HasField("metadata"):
                current_image = {
                    "metadata": {
                        "username": chunk.metadata.username,
                        "image_name": chunk.metadata.image_name,
                        "file_type": chunk.metadata.file_type,
                        "size": chunk.metadata.size
                    },
                    "data": bytearray()
                }
                images.append(current_image)
            else:
                current_image["data"].extend(chunk.image_data)
        
        return True, images

    @retry_on_failure()
    def fetch_albums(self):
        '''
            Fetches all albums for the current user.
        '''
        request = {
            "username": self.username,
            "from_client": True,
        }
        request = server_pb2.FetchUserAlbumsRequest(**request)
        res = self.stubs[self.leader].FetchUserAlbums(request)
        return res.success, res.albums
    

    @retry_on_failure()
    def get_album_editors(self, album_name):
        """Get the list of editors for an album."""
        request = {
            "username": self.username,
            "album_name": album_name,
            "from_client": True,
        }
        request = server_pb2.FetchAlbumEditorsRequest(**request)
        res = self.stubs[self.leader].FetchAlbumEditors(request)
        
        if res.success:
            return res.success, res.editors
        else:
            return res.success, res.message
 