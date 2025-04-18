from concurrent import futures
import time
import grpc
import sys
# for pytest to properly import quirks
try:
    from server.server import Server
except ModuleNotFoundError:
    from server import Server
from dotenv import load_dotenv
sys.path.append('../protos')
import server_pb2 
import server_pb2_grpc
import client_listener_pb2
import client_listener_pb2_grpc
from account_management import check_if_online, create_account, fetch_sent_messages, list_accounts, login, logout, logout_all_users, read_messages, send_offline_message, delete_account, delete_message
import threading
import os

load_dotenv(override=True)

def serve(server_object):
    '''
        Starts the server and listens for incoming requests
    '''

    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        server_pb2_grpc.add_ServerServicer_to_server(server_object, server)
        address = f"{server_object.host}:{server_object.port}"
        server.add_insecure_port(address)
        server.start()
        print(f"Running server on host: {server_object.host} and port: {server_object.port}")
        server.wait_for_termination()

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
        logout_all_users(server_object.db_path)
        server.stop(0)

def connect(server_object):
    '''
        Connects to other servers in the cluster
    '''
    print("Attempting to Connect to other servers")

    # Create a channel to connect to other servers
    for peer_id in range(3):
        if peer_id == server_object.id:
            continue

        host = os.getenv(f"SERVER_HOST_{peer_id}")
        port = int(os.getenv(f"SERVER_PORT_{peer_id}"))

        print(f"Connecting to server {peer_id} at {host}:{port}")

        MAX_RETRIES = 20
        retry_delay = 2  # seconds

        # Attempt to connect to the server of client {id}
        for attempt in range(MAX_RETRIES):
            try:
                channel = grpc.insecure_channel(f"{host}:{port}")

                # Wait for the channel to be ready
                grpc.channel_ready_future(channel).result(timeout=retry_delay)

                stub = server_pb2_grpc.ServerStub(channel)
                server_object.server_stubs[peer_id] = stub

                # Begin sending heartbeats to the connected server
                threading.Thread(target=server_object.begin_heartbeats, args=(peer_id,), daemon=True).start()
                break
            

            except grpc.FutureTimeoutError as e:
                # Connection Attempt Timed Out
                if attempt == MAX_RETRIES - 1:
                    print(f"Failed to connect to server {peer_id} after {MAX_RETRIES} attempts.")
                    raise ConnectionError(f"Unable to connect to server {peer_id} after {MAX_RETRIES} attempts.")

                time.sleep(retry_delay)

        print(f"Connected to server {peer_id}")

    server_object.local_alive_servers = set(server_object.server_stubs.keys())
    server_object.global_alive_servers = set(server_object.server_stubs.keys())
    server_object.local_alive_servers.add(server_object.id)
    server_object.global_alive_servers.add(server_object.id)
    
    print("Connected to all servers")          

def initialize(id, db_path):
    print("host and port", f"SERVER_HOST_{id}", f"SERVER_PORT_{id}")
    host, port = os.getenv(f"SERVER_HOST_{id}"), int(os.getenv(f"SERVER_PORT_{id}"))
    server_object = Server(id, host, port, db_path)

    # Set Server 0 As Leader
    if id == 0:
        server_object.is_leader = True
        server_object.current_leader = 0
        print("Server is leader")
    else:
        server_object.current_leader = 0
        print("Server is not leader")

    # Connect to other servers in background thread
    threading.Thread(target=connect, args=(server_object,), daemon=True).start()

    serve(server_object)
    server_object.cleanup()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python driver.py <server_id> <optional: db_path>")
        sys.exit(1)
    
    # Get command line arguments
    server_id = sys.argv[1]
    db_path = None
    if len(sys.argv) == 3:
        db_path = sys.argv[2]

    # Validate Command Line Arguments
    if not server_id.isdigit():
        print("Invalid server ID. Server ID must be an integer.")
        sys.exit(1)

    server_id = int(server_id)
    if server_id not in [0, 1, 2]:
        print("Invalid server ID. Please provide 0, 1, or 2.")
        sys.exit(1)

    initialize(server_id, db_path)
