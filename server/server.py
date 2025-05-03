from concurrent import futures
from debouncer import Debouncer
import time
import grpc
import sys
sys.path.append('../protos')
import server_pb2 
import server_pb2_grpc
import client_listener_pb2
import client_listener_pb2_grpc
from account_management import add_album_editor, check_if_online, create_account, create_album, delete_album, delete_image, fetch_album_editors, fetch_albums, fetch_photos, list_accounts, login, logout, logout_all_users, remove_album_editor, delete_account, upload_image
import threading
import os

class Server(server_pb2_grpc.ServerServicer):
    def __init__(self, id, host, port, db_path=None):
        # Map of username to client stub for sending messages to clients that must be delivered immediately
        self.stub_map = {} 

        # Map of Stubs to Peer Servers 
        self.server_stubs = {}

        self.id = id
        self.is_leader = False
        self.db_path = None

        self.host = host
        self.port = port

        if db_path:
            if os.path.exists(db_path):
                self.db_path = db_path
            else:
                print("Database does not exist. Using default instead.")
        else:
            self.db_path = self._get_default_db_pathname(id)


        self.current_leader = None  # id of the current leader of the server cluster
        
        self.heartbeat_interval = 2  
        self.heartbeat_timeout = 6
        self.local_alive_servers = set([0, 1, 2])    # Set of servers that this server believes are alive
        self.global_alive_servers = set([0, 1, 2])   # Set of servers that all servers believe are alive

    def Heartbeat(self, request_iterator, context):
        debouncer = Debouncer(
            lambda: self._handle_server_death(server_id),
            self.heartbeat_timeout
        )

        for request in request_iterator:
            server_id = request.server_id
            timestamp = request.timestamp
            # print(f"[Monitor] Received heartbeat from server {server_id} at time {timestamp}")

            debouncer() # Reset countdown until assumption of server death
            
        return server_pb2.HeartbeatResponse(acknowledged=True)
    
    def ConfirmServerDeath(self, request, context):
        '''
            Checks if the current server believes the specified server is alive or dead.
            This request is only received from the other servers when they believe a server to be dead. 
            As a result, if the local server believes the specified server to be dead, it can be safely assumed
            that all other servers also believe it to be dead.
        '''
        server_id = request.server_id
        is_dead = server_id not in self.local_alive_servers

        # If the server is believed to be dead locally, it is also dead globally
        if is_dead:
            self.global_alive_servers.discard(server_id)
            print(f"[Consensus] All reachable peers agree server {server_id} is dead. In ConfirmServerDeath...")
            # Elect new leader if necessary
            if server_id == self.current_leader:
                self._elect_new_leader(server_id)

        return server_pb2.StatusResponse(is_dead=is_dead)
    
    def _handle_server_death(self, server_id):
        '''
            Handles the death of a server 
        '''
        print(f"[Monitor] Suspecting Server {server_id} is DEAD at time", time.time())

        if server_id not in self.local_alive_servers:
            return  # Already handled

        # Locally, treat server as dead
        self.local_alive_servers.remove(server_id)
        self.server_stubs.pop(server_id, None)

        MAXIMUM_RETRIES = 3
        RETRY_DELAY = 1  # seconds

        agreement = []
        for _ in range(MAXIMUM_RETRIES):
            # Check with all other servers to see if they agree that this server is dead
            for peer_id in range(3):
                # Skip dying server and already dead servers
                if peer_id == server_id or peer_id not in self.local_alive_servers:
                    continue

                stub = self.server_stubs.get(peer_id)
                if not stub:
                    continue

                try:
                    response = stub.ConfirmServerDeath(server_pb2.StatusRequest(server_id=server_id))
                    agreement.append(response.is_dead)
                except Exception as e:
                    print(f"[Consensus] Could not reach server {peer_id} to confirm death of server {server_id}. This is not necessarily unexpected behavior.")
            
            # Received response from peers, break out of loop
            if agreement:
                break
            
            # No response from any peers, retry with delay to check for temporary communication errors
            time.sleep(RETRY_DELAY)

        # Check if all reachable peers agree on the server's death
        if all(agreement):
            print(f"[Consensus] All reachable peers agree server {server_id} is dead.")
            self.global_alive_servers.discard(server_id)
            
            # Elect new leader if all servers agree that leader is dead or if there are no other servers left
            if server_id == self.current_leader:
                self._elect_new_leader(server_id)

        
    def _elect_new_leader(self, server_id):
        print(f"[Leader Election] Leader {server_id} has died. Electing new leader...")
        new_leader = min(self.global_alive_servers)
        self.current_leader = new_leader
        self.is_leader = (self.id == new_leader)
        if self.is_leader:
            print(f"[Leader Election] I am the new leader (Server {self.id})")
        else:
            print(f"[Leader Election] New leader is Server {new_leader}")
    
    def begin_heartbeats(self, server_id):
        '''
            Begins sending heartbeats to specified server
        '''
        try:
            if server_id not in self.server_stubs:
                print(f"[Heartbeat] Server {server_id} is not connected.")
                return
            
            if server_id not in self.local_alive_servers:
                print(f"[Heartbeat] Server {server_id} is considered DEAD. Declining to set up heartbeat messages to the server.")
                return
            
            print(f"[Heartbeat] Beginning to send heartbeats to server {server_id} at time", time.time())
            stub = self.server_stubs[server_id]

            # Begin sending stream of heartbeat messages to the server
            stub.Heartbeat(self._generate_heartbeat_requests())
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"This is the standard error raised when a server dies and the gRPC connection is lost. We will ignore this error here to stay more authentic to the nature of the assignment (since we assume that we are supposed to be able to handle the silent failure of a server)")
                return
            
            print(f"[Heartbeat] Error sending heartbeat to server {server_id}: {e}")
        
    def _generate_heartbeat_requests(self):
        '''
            Generates a stream of heartbeat requests to be sent to other servers
        '''
        while True:
            heartbeat_request = server_pb2.HeartbeatRequest(
                server_id=self.id,
                timestamp=int(time.time())
            )
            yield heartbeat_request

            time.sleep(self.heartbeat_interval)

    def CurrentLeader(self, request, context):
        '''
            Returns the current leader of the server cluster
        '''
        print(f"Received request to identify current leader from {self.id}")
        response = server_pb2.CurrentLeaderResponse(leader=self.current_leader)
        return response
    
    def Signup(self, request, context):
        username = request.username
        password = request.password
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response

        print(f"Received signup request from {username}")
        res = create_account(username, password, self.db_path)

        if res["success"] and self.is_leader:
            # Notify other servers of new user
            for stub in self.server_stubs.values():
                request = server_pb2.UserAuthRequest(
                    username=username, 
                    password=password,
                    from_client=False,
                )
                temp_res = stub.Signup(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of new user {username}")
                    print(res.message)
                    raise Exception(f"Failed to notify server {stub} of new user {username}")

        return server_pb2.StandardServerResponse(**res)
    
    def Login(self, request, context):
        username = request.username
        password = request.password
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")

            standard_server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            server_response = server_pb2.UserLoginResponse()
            server_response.failure.CopyFrom(standard_server_response)
            return server_response

        
        print(f"Received login request from {username}")
        res = login(username, password, self.db_path)

        server_response = server_pb2.UserLoginResponse() 
        if res["success"]:
            user_login_success = server_pb2.UserLoginSuccess(**res)  # create UserLoginSuccess
            server_response.success.CopyFrom(user_login_success)  # assign to login_response

            if self.is_leader:
                # Notify other servers of new user
                for stub in self.server_stubs.values():
                    request = server_pb2.UserAuthRequest(
                        username=username, 
                        password=password,
                        from_client=False
                    )
                    temp_res = stub.Login(request)
                    if not temp_res.success:
                        print(f"Failed to notify server {stub} of new user {username}")
                        print(res.message)
                        raise Exception(f"Failed to notify server {stub} of new user {username}")
        else:
            standard_server_response = server_pb2.StandardServerResponse(**res)  # create StandardServerResponse
            server_response.failure.CopyFrom(standard_server_response)  # assign to login_response
        return server_response
    
    def Logout(self, request, context):
        username = request.username
        from_client = request.from_client
        print(f"Received logout request from {username}")

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        
        res = logout(username, self.db_path)

        if res["success"] and self.is_leader:
            # Notify other servers of logout
            for stub in self.server_stubs.values():
                request = server_pb2.UserLogoutRequest(
                    username=username,
                    from_client=False
                )

                temp_res = stub.Logout(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of new user {username}")
                    print(res.message)
                    raise Exception(f"Failed to notify server {stub} of new user {username}")


        if username in self.stub_map:
            del self.stub_map[username]

        return server_pb2.StandardServerResponse(**res)

    def ListUsernames(self, request, context):
        username_pattern = request.username_pattern
        print("Received list accounts request")
        res = list_accounts(username_pattern, self.db_path)
        
        server_response = server_pb2.ListUsernamesResponse()
        if res["success"]:
            usernames = server_pb2.ListUsernames(
                success = res["success"],
                message = res["message"],
                matches = res["matches"]
            )
            server_response.success.CopyFrom(usernames)

        else:
            failure = server_pb2.StandardServerResponse(
                success=res["success"],
                message=res["message"]
            )
            server_response.failure.CopyFrom(failure)
        
        return server_response
    
    def RegisterClient(self, request, context):
        '''
            Registers a client stub to the server for sending messages to the client
        '''
        username = request.username
        host = request.host
        port = request.port
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response

        channel = grpc.insecure_channel(f"{host}:{port}")
        stub = client_listener_pb2_grpc.Client_ListenerStub(channel)
        print(f"Received register client request from {username}")

        self.stub_map[username] = stub

        if self.is_leader:
            # Notify other servers of new client
            for stub in self.server_stubs.values():
                request = server_pb2.RegisterClientRequest(
                    username=username, 
                    host=host, 
                    port=port,
                    from_client=False
                )
                temp_res = stub.RegisterClient(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of new client registration {username}")
                    print(temp_res.message)
                    raise Exception(f"Failed to notify server {stub} of new client registration {username}")
                
        return server_pb2.StandardServerResponse(success=True, message= "Registered successfully")

    def DeleteAccount(self, request, context):
        username = request.username
        from_client = request.from_client
        print(f"Received delete account request from {username}")

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        
        res = delete_account(username, self.db_path)

        if res["success"] and self.is_leader:
            # Notify other servers of delete account
            for stub in self.server_stubs.values():
                request = server_pb2.DeleteAccountRequest(
                    username=username,
                    from_client=False
                )
                temp_res = stub.DeleteAccount(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of delete account for {username}")
                    print(res.message)
                    raise Exception(f"Failed to notify server {stub} of delete account for {username}")

        if username in self.stub_map:
            del self.stub_map[username]
        
        return server_pb2.StandardServerResponse(**res)

    def UploadImage(self, request_iterator, context):
        '''
            Handles image upload requests from clients.
            This is a placeholder for the actual image upload logic.
        '''
        for request in request_iterator:
            if request.from_client and not self.is_leader:
                print(f"Server {self.id} is not the leader. Rejecting request.")
                return server_pb2.StandardServerResponse(
                    success=False, 
                    message="You made a request to a non-leader server. Please try again later."
                )

            if request.HasField("metadata"):
                metadata = request.metadata
                username = metadata.username
                image_name = metadata.image_name
                size = metadata.size
                file_type = metadata.file_type
                album = metadata.album
                print(f"Received metadata for image upload: {metadata}")
                image_data = bytearray()
            else:
                image_data.extend(request.image_data)
                
        res = upload_image(username, image_name, file_type, album, self.db_path, image_data)
        
        # Forward result to other servers if necessary
        if res["success"] and self.is_leader:
            for stub in self.server_stubs.values():
                print("metadata", metadata)
                metadata = {"username": username, "image_name": image_name, "file_type": file_type, }
                temp_res = stub.UploadImage(
                    self._generate_image_stream(
                        album, 
                        [{"image_path": res["image_path"], "metadata": metadata}]
                    )
                )
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of image upload for {username}")
                    print(res.message)
                    raise Exception(f"Failed to notify server {stub} of image upload for {username}")

        print(f"Image upload result: {res}")
        return server_pb2.StandardServerResponse(success=res["success"], message=res["message"])
    

    def CreateAlbum(self, request, context):
        '''
            Creates a new photo album for the user
        '''
        username = request.username
        album_name = request.album_name
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        
        print(f"Received create album request from {username} for album {album_name}")
        res = create_album(username, album_name, self.db_path)

        if res["success"] and self.is_leader:
            # Notify other servers of new album
            for stub in self.server_stubs.values():
                request = server_pb2.CreateAlbumRequest(
                    username=username, 
                    album_name=album_name,
                    from_client=False
                )
                temp_res = stub.CreateAlbum(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of new album {album_name} for {username}")
                    print(res.message)
                    raise Exception(f"Failed to notify server {stub} of new album {album_name} for {username}")

        return server_pb2.StandardServerResponse(**res)

    def AddAlbumEditor(self, request, context):
        '''
            Adds a user as an editor to the specified album
        '''
        requestor_username = request.requestor_username  # The username of the user making the request
        editor_username = request.editor_username  # The username of the user being added as an editor
        album_name = request.album_name
        from_client = request.from_client  

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response

        res = add_album_editor(requestor_username, editor_username, album_name, self.db_path)

        if res["success"] and self.is_leader:
            # Notify other servers of new album editor
            for stub in self.server_stubs.values():
                request = server_pb2.AddAlbumEditorRequest(
                    requestor_username=requestor_username,
                    editor_username=editor_username,
                    album_name=album_name,
                    from_client=False
                )
                temp_res = stub.AddAlbumEditor(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of new album editor {editor_username} for {album_name}")
                    print(temp_res.message)
                    raise Exception(f"Failed to notify server {stub} of new album editor {editor_username} for {album_name}")

        return server_pb2.StandardServerResponse(**res)

    def RemoveAlbumEditor(self, request, context):
        '''
            Removes a user as an editor from the specified album
        '''

        requestor_username = request.requestor_username  # The username of the user making the request
        editor_username = request.editor_username  # The username of the user being added as an editor
        album_name = request.album_name
        from_client = request.from_client  

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response

        res = remove_album_editor(requestor_username, editor_username, album_name, self.db_path)

        if res["success"] and self.is_leader:
            # Notify other servers of new album editor
            for stub in self.server_stubs.values():
                request = server_pb2.RemoveAlbumEditorRequest(
                    requestor_username=requestor_username,
                    editor_username=editor_username,
                    album_name=album_name,
                    from_client=False
                )
                temp_res = stub.RemoveAlbumEditor(request)
                if not temp_res.success:
                    print(f"Failed to notify server {stub} of removed album editor {editor_username} for {album_name}")
                    print(temp_res.message)
                    raise Exception(f"Failed to notify server {stub} of new album editor {editor_username} for {album_name}")

        return server_pb2.StandardServerResponse(**res)

    def DeleteAlbum(self, request, context):
        '''
            Deletes the specified album
        '''
        username = request.username
        album_name = request.album_name
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        
        print(f"Received delete album request from {username} for album {album_name}")

        # Leader: replicate to followers first
        if self.is_leader:
            for server_id, stub in self.server_stubs.items():
                try:
                    follower_request = server_pb2.DeleteAlbumRequest(
                        username=username,
                        album_name=album_name,
                        from_client=False
                    )
                    temp_res = stub.DeleteAlbum(follower_request)
                    if not temp_res.success:
                        print(f"[DeleteAlbum] Replication failed on follower {server_id}: {temp_res.message}")
                        return server_pb2.StandardServerResponse(success=False, message=f"Replication failed on follower {server_id}: {temp_res.message}")
                except Exception as e:
                    print(f"[DeleteAlbum] Exception while notifying follower {server_id}: {e}")
                    return server_pb2.StandardServerResponse(success=False, message=f"Replication error: {e}")

        # Only now perform the local delete
        res = delete_album(username, album_name, self.db_path)
        return server_pb2.StandardServerResponse(**res)
    
    def DeleteImage(self, request, context):
        '''
            Deletes the specified image from the album
        '''
        username = request.username
        album_name = request.album_name
        image_name = request.image_name
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        print(f"Received delete image request from {username} for image {image_name} in album {album_name}")

        # Leader: replicate to followers first
        if self.is_leader:
            for server_id, stub in self.server_stubs.items():
                try:
                    follower_request = server_pb2.DeleteImageRequest(
                        username=username,
                        album_name=album_name,
                        image_name=image_name,
                        from_client=False
                    )
                    temp_res = stub.DeleteImage(follower_request)
                    if not temp_res.success:
                        print(f"[DeleteImage] Replication failed on follower {server_id}: {temp_res.message}")
                        return server_pb2.StandardServerResponse(success=False, message=f"Replication failed on follower {server_id}: {temp_res.message}")
                except Exception as e:
                    print(f"[DeleteImage] Exception while notifying follower {server_id}: {e}")
                    return server_pb2.StandardServerResponse(success=False, message=f"Replication error: {e}")

        # Only now perform the local delete
        res = delete_image(username, image_name, album_name, self.db_path)
        return server_pb2.StandardServerResponse(**res)
    
    def FetchPhotos(self, request, context):
        '''
            Fetches photos from the specified album
        '''
        username = request.username
        album_name = request.album_name
        page = request.page
        page_size = request.page_size
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        
        print(f"Received fetch photos request from {username} for album {album_name}")
        res = fetch_photos(username, album_name, page, page_size, self.db_path)
        
        if not res["success"]:
            # If the operation failed, return an empty stream
            return self._generate_image_stream(album_name, [])
            
        return self._generate_image_stream(album_name, res["images"])
    
    def FetchUserAlbums(self, request, context):
        '''
            Fetches all albums for the specified user
        '''
        username = request.username
        from_client = request.from_client

        # If non-leader server receives request from a client, reject
        if from_client and not self.is_leader:
            print(f"Server {self.id} is not the leader. Rejecting request.")
            server_response = server_pb2.StandardServerResponse(
                success=False, 
                message="You made a request to a non-leader server. Please try again later."
            )
            return server_response
        
        print(f"Received fetch albums request from {username}")
        res = fetch_albums(username, self.db_path)
        return server_pb2.FetchUserAlbumsResponse(**res)
        
    def _generate_image_stream(self, album_name, images):
        '''
            Generates a stream of image data to be sent to the client.
            album_name (str): The name of the album to fetch images from.
            images (list): A list of dictionaries containing image metadata and path to image.
        '''
        for image in images:
            # Send image metadata first
            image_path = image["image_path"]
            metadata = image["metadata"]

            metadata_message = server_pb2.ImageMetadata(
                username=metadata['username'],
                album=album_name,
                image_name=metadata['image_name'],
                size=-1, # TODO: UPDATE THIS PLACEHOLDER
                file_type=metadata['file_type']
            )
            
            server_response = server_pb2.ImageChunk()
            server_response.metadata.CopyFrom(metadata_message)
            server_response.from_client = False

            yield server_response

            # Read the image data in chunks
            with open(image_path, 'rb') as f:
                while True:
                    CHUNK_SIZE = 1024 * 1024 # 1 megabyte
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    yield server_pb2.ImageChunk(
                        image_data=chunk,
                        from_client=False,
                    )

    def FetchAlbumEditors(self, request, context):
        '''
            Fetches all editors for the specified album
        '''
        print('HELLOOOOOOO')
        username = request.username
        album_name = request.album_name

        print(f"Received fetch album editors request from {username} for album {album_name}")
        res = fetch_album_editors(username, album_name, self.db_path)
        
        if not res["success"]:
            return server_pb2.FetchAlbumEditorsResponse(success=False, message=res["message"], editors=[])

        return server_pb2.FetchAlbumEditorsResponse(**res)

    def cleanup(self):
        '''
            Cleans up the server by logging out all users
        '''
        print("Cleaning up server")
        logout_all_users(self.db_path)
        print("Logged out all users")
        print("Server cleanup complete")
    
    def  _get_default_db_pathname(self, id):
        current_dir = os.path.dirname(__file__)
        base_dir = os.path.dirname(current_dir)
        db_pathname = os.path.join(base_dir, f'db_{id}')

        return db_pathname
