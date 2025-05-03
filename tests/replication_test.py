import pytest
import time
from unittest.mock import patch, MagicMock
import sys
import os
import grpc
import threading
import tempfile
from concurrent import futures
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../server')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos')))
from client import Client
from server.server import Server
from driver import serve, connect
import server_pb2
import server_pb2_grpc


@pytest.fixture(scope="module", autouse=True)
def setup_env_vars():
    os.environ["SERVER_HOST_0"] = "localhost"
    os.environ["SERVER_PORT_0"] = "5000"
    os.environ["SERVER_HOST_1"] = "localhost"
    os.environ["SERVER_PORT_1"] = "5001"
    os.environ["SERVER_HOST_2"] = "localhost"
    os.environ["SERVER_PORT_2"] = "5002"

@patch("driver.grpc.insecure_channel")
@patch("driver.grpc.channel_ready_future")
@patch("driver.server_pb2_grpc.ServerStub")
def create_connected_server(mock_stub, mock_ready, mock_channel):
    mock_ready.return_value.result.return_value = None
    mock_stub.return_value = MagicMock()
    mock_channel.return_value = MagicMock()

    server = Server(id=0, host="localhost", port="5000")
    connect(server)
    return server

def test_server_connection():
    with patch("driver.grpc.insecure_channel") as ch, \
         patch("driver.grpc.channel_ready_future") as ready, \
         patch("driver.server_pb2_grpc.ServerStub") as stub:

        ready.return_value.result.return_value = None
        stub.return_value = MagicMock()
        ch.return_value = MagicMock()

        server = Server(id=0, host="localhost", port="5000")
        connect(server)

        assert len(server.server_stubs) == 2
        assert server.local_alive_servers == {0, 1, 2}
        assert server.global_alive_servers == {0, 1, 2}

def test_death_of_non_leader():
    with patch("driver.grpc.insecure_channel") as ch, \
         patch("driver.grpc.channel_ready_future") as ready, \
         patch("driver.server_pb2_grpc.ServerStub") as stub:

        ready.return_value.result.return_value = None
        stub.return_value = MagicMock()
        ch.return_value = MagicMock()

        leader = Server(id=0, host="localhost", port="5000")
        follower = Server(id=1, host="localhost", port="5001")

        connect(leader)

        # Sanity check after connection
        assert leader.local_alive_servers == {0, 1, 2}
        assert leader.global_alive_servers == {0, 1, 2}

        # Simulate follower sees server 2 as dead
        follower.local_alive_servers.remove(2)
        # Simulate leader also believes server 2 is dead
        leader.local_alive_servers.remove(2)

        # Follower tells leader about server 2
        request = server_pb2.StatusRequest(server_id=2)
        response = leader.ConfirmServerDeath(request, context=None)

        assert 2 not in leader.global_alive_servers
        assert response.is_dead

def test_leader_death_and_reelection():
    with patch("driver.grpc.insecure_channel") as ch, \
         patch("driver.grpc.channel_ready_future") as ready, \
         patch("driver.server_pb2_grpc.ServerStub") as stub:

        # Mock networking
        ready.return_value.result.return_value = None
        stub.return_value = MagicMock()
        ch.return_value = MagicMock()

        # Initialize 3 servers
        s0 = Server(id=0, host="localhost", port="5000")  # original leader
        s1 = Server(id=1, host="localhost", port="5001")
        s2 = Server(id=2, host="localhost", port="5002")

        # Connect s1 and s2 (simulate real startup behavior)
        connect(s1)
        connect(s2)

        # All servers believe s0 is the initial leader
        for s in [s1, s2]:
            s.current_leader = 0
            s.global_alive_servers = {0, 1, 2}
            s.local_alive_servers = {0, 1, 2}

        # Simulate both s1 and s2 detect s0 is dead
        for s in [s1, s2]:
            s.local_alive_servers.remove(0)

        # Each remaining server calls ConfirmServerDeath to initiate consensus
        request = server_pb2.StatusRequest(server_id=0)
        s1.ConfirmServerDeath(request, context=None)
        s2.ConfirmServerDeath(request, context=None)

        # Assert server 0 is gone from global alive set
        assert 0 not in s1.global_alive_servers
        assert 0 not in s2.global_alive_servers

        # Check that new leader is elected and both servers agree
        new_leader_expected = min(s2.global_alive_servers)
        assert s1.current_leader == new_leader_expected
        assert s2.current_leader == new_leader_expected

        # Check that the new leader has the correct is_leader flag
        if s1.id == new_leader_expected:
            assert s1.is_leader
            assert not s2.is_leader
        else:
            assert s2.is_leader
            assert not s1.is_leader

def test_two_servers_die():
    with patch("driver.grpc.insecure_channel") as ch, \
         patch("driver.grpc.channel_ready_future") as ready, \
         patch("driver.server_pb2_grpc.ServerStub") as stub:

        # Mock networking
        ready.return_value.result.return_value = None
        stub.return_value = MagicMock()
        ch.return_value = MagicMock()

        # Set up 3 servers
        s0 = Server(id=0, host="localhost", port="5000")  # leader
        s1 = Server(id=1, host="localhost", port="5001")
        s2 = Server(id=2, host="localhost", port="5002")

        # Connect the surviving server (s2)
        connect(s2)

        # Initially everyone thinks s0 is leader and all are alive
        s2.current_leader = 0
        s2.global_alive_servers = {0, 1, 2}
        s2.local_alive_servers = {0, 1, 2}

        # Simulate both s0 and s1 die — remove from local_alive
        s2.local_alive_servers.remove(0)
        s2.local_alive_servers.remove(1)

        # Confirm server 0 death
        req_0 = server_pb2.StatusRequest(server_id=0)
        res_0 = s2.ConfirmServerDeath(req_0, context=None)
        assert res_0.is_dead

        # Confirm server 1 death
        req_1 = server_pb2.StatusRequest(server_id=1)
        res_1 = s2.ConfirmServerDeath(req_1, context=None)
        assert res_1.is_dead

        # Final checks
        assert s2.global_alive_servers == {2}
        assert s2.current_leader == 2
        assert s2.is_leader

def test_decorator_triggers_leader_update_on_failure():
    with patch("client.grpc.insecure_channel") as ch, \
         patch("client.grpc.channel_ready_future") as ready, \
         patch("client.server_pb2_grpc.ServerStub") as stub:

        ready.return_value.result.return_value = None

        # Create fake stubs
        stub0 = MagicMock()
        stub1 = MagicMock()
        stub2 = MagicMock()

        # All CurrentLeader calls return leader = 1
        stub0.CurrentLeader.return_value = MagicMock(leader=1)
        stub1.CurrentLeader.return_value = MagicMock(leader=1)
        stub2.CurrentLeader.return_value = MagicMock(leader=1)

        # stub0 fails on signup — forces retry
        stub0.Signup.side_effect = grpc.RpcError("RPC failed")

        # stub1 succeeds
        stub1.Signup.return_value.success = True
        stub1.Signup.return_value.message = "Signup successful"

        # Channel + stub mapping
        def fake_channel_creator(addr):
            channel = MagicMock()
            channel.target.return_value = addr
            return channel
        ch.side_effect = fake_channel_creator

        def stub_selector(channel):
            target = channel.target()
            if "5000" in target:
                return stub0
            elif "5001" in target:
                return stub1
            elif "5002" in target:
                return stub2
            return MagicMock()
        stub.side_effect = stub_selector

        # Set environment
        os.environ["SERVER_HOST_0"] = "localhost"
        os.environ["SERVER_PORT_0"] = "5000"
        os.environ["SERVER_HOST_1"] = "localhost"
        os.environ["SERVER_PORT_1"] = "5001"
        os.environ["SERVER_HOST_2"] = "localhost"
        os.environ["SERVER_PORT_2"] = "5002"

        # Create client and simulate wrong initial leader
        client = Client(server_host="localhost", server_port="1234")
        client.leader = 0  # wrong leader

        # Signup triggers decorator-based recovery
        success, message = client.signup("testuser", "testpass")

        assert success
        assert message == "Signup successful"
        stub1.Signup.assert_called_once()
        stub0.Signup.assert_called_once()  # first call failed