import pytest
from unittest.mock import patch, mock_open
import json
import os
import sys
import bcrypt
import uuid
import selectors
sys.path.append('../')
from server.account_management import load_user_data, save_user_data, username_exists, create_account, login, logout, list_accounts, check_if_online, get_db_pathname, logout_all_users, delete_account

DB_PATH = '/mock/path'

def test_load_user_data_file_exists():
    mock_data = {"testuser": {"password": "hashed_password"}}
    with patch("os.path.exists") as mock_exists, \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        mock_exists.return_value = True
        result = load_user_data(DB_PATH)
        assert result == mock_data

def test_load_user_data_file_not_exists():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        result = load_user_data(DB_PATH)
        assert result == {}

def test_save_user_data():
    users = {"testuser": {"password": "hashed_password"}}
    with patch("builtins.open", mock_open()) as mock_file:
        save_user_data(users, DB_PATH)
        mock_file.assert_called_once_with(os.path.join(DB_PATH, "user_data.json"), "w")
        handle = mock_file()
        handle.write.assert_any_call('{')
        handle.write.assert_any_call('"testuser"')
        handle.write.assert_any_call(': ')
        handle.write.assert_any_call('{')
        handle.write.assert_any_call('"password"')
        handle.write.assert_any_call(': ')
        handle.write.assert_any_call('"hashed_password"')
        handle.write.assert_any_call('}')
        handle.write.assert_any_call('}')

def test_username_exists_true():
    with patch('server.account_management.load_user_data') as mock_load_user_data:
        mock_load_user_data.return_value = {'testuser': {}}
        assert username_exists('testuser', DB_PATH) == True

def test_username_exists_false():
    with patch('server.account_management.load_user_data') as mock_load_user_data:
        mock_load_user_data.return_value = {'anotheruser': {}}
        assert username_exists('testuser', DB_PATH) == False

def test_username_exists_empty():
    with patch('server.account_management.load_user_data') as mock_load_user_data:
        mock_load_user_data.return_value = {}
        assert username_exists('testuser', DB_PATH) == False

def test_create_account_success():
    dummy_users = {}
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.save_user_data') as mock_save_user_data, \
         patch('server.account_management.username_exists', return_value=False), \
         patch('server.account_management.get_db_pathname', return_value=DB_PATH), \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('bcrypt.hashpw', return_value=b'hashed_password'):
        
        result = create_account('testuser', 'password123', DB_PATH)
        
        assert result == {
            "success": True,
            "message": "Account created successfully."
        }

def test_create_account_empty_username_password():
    result = create_account('', '', DB_PATH)
    assert result == {
        "success": False,
        "message": "Username and/or password cannot be empty.",
    }

def test_create_account_username_exists():
    dummy_users = {'testuser': {}}
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.username_exists', return_value=True):
        
        result = create_account('testuser', 'password123', DB_PATH)
        
        assert result == {
            "success": False,
            "message": "Username already exists. Please try again.",
        }

def test_login_success():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'online': False
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.save_user_data') as mock_save_user_data, \
         patch('server.account_management.check_if_online', return_value=False), \
         patch('server.account_management.username_exists', return_value=True), \
         patch('server.account_management.get_db_pathname', return_value=DB_PATH), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data='[]')) as mock_file:
        
        result = login('testuser', 'password123', DB_PATH)
        
        assert result == {
            "success": True,
            "message": "Login successful."
        }

def test_login_user_already_logged_in():
    with patch('server.account_management.check_if_online', return_value=True):
        result = login('testuser', 'password123', DB_PATH)
        assert result == {
            "success": False,
            "message": "User is already logged in."
        }

def test_login_incorrect_username_password():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'online': False
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.username_exists', return_value=True):
        
        result = login('testuser', 'wrongpassword', DB_PATH)
        assert result == {
            "success": False,
            "message": "Incorrect username or password. Please try again.",
        }

def test_login_username_does_not_exist():
    with patch('server.account_management.username_exists', return_value=False):
        result = login('nonexistentuser', 'password123', DB_PATH)
        assert result == {
            "success": False,
            "message": "Incorrect username or password. Please try again."
        }

def test_logout_success():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': 'hashed_password',
            'online': True
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.save_user_data') as mock_save_user_data, \
         patch('server.account_management.username_exists', return_value=True):
        
        result = logout('testuser', DB_PATH)
        
        assert result == {
            "success": True,
            "message": "Logout successful."
        }
        mock_save_user_data.assert_called_once_with({
            'testuser': {
                'username': 'testuser',
                'password': 'hashed_password',
                'online': False
            }
        }, DB_PATH)

def test_logout_username_does_not_exist():
    dummy_users = {}
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.username_exists', return_value=False):
        
        result = logout('nonexistentuser', DB_PATH)
        
        assert result == {
            "success": False,
            "message": "Username does not exist.",
        }

def test_list_accounts_success():
    dummy_users = {
        'testuser1': {},
        'testuser2': {},
        'anotheruser': {}
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users):
        result = list_accounts('testuser', DB_PATH)
        assert result == {
            "success": True,
            "message": "Accounts listed successfully.",
            "matches": ['testuser1', 'testuser2']
        }

def test_list_accounts_no_matches():
    dummy_users = {
        'testuser1': {},
        'testuser2': {},
        'anotheruser': {}
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users):
        result = list_accounts('nomatch', DB_PATH)
        assert result == {
            "success": True,
            "message": "Accounts listed successfully.",
            "matches": [],
        }

def test_check_if_online_user_online():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': 'hashed_password',
            'online': True
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users):
        assert check_if_online('testuser', DB_PATH) == True

def test_check_if_online_user_offline():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': 'hashed_password',
            'online': False,
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users):
        assert check_if_online('testuser', DB_PATH) == False

def test_check_if_online_user_does_not_exist():
    dummy_users = {}
    with patch('server.account_management.load_user_data', return_value=dummy_users):
        assert check_if_online('nonexistentuser', DB_PATH) == False

def test_logout_all_users():
    dummy_users = {
        'user1': {
            'username': 'user1',
            'password': 'hashed_password',
            'online': True,
            'host': '127.0.0.1',
            'port': 12345
        },
        'user2': {
            'username': 'user2',
            'password': 'hashed_password',
            'online': True,
            'host': '127.0.0.1',
            'port': 12345
        }
    }
    expected_users = {
        'user1': {
            'username': 'user1',
            'password': 'hashed_password',
            'online': False,
            'host': '',
            'port': ''
        },
        'user2': {
            'username': 'user2',
            'password': 'hashed_password',
            'online': False,
            'host': '',
            'port': ''
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.save_user_data') as mock_save_user_data:
        
        logout_all_users(DB_PATH)
        
        mock_save_user_data.assert_called_once_with(expected_users, DB_PATH)

def test_delete_account_success():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': 'hashed_password',
            'online': True
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.save_user_data') as mock_save_user_data, \
         patch('server.account_management.get_db_pathname', return_value=DB_PATH), \
         patch('os.path.exists', return_value=True), \
         patch('os.remove') as mock_remove:
        
        result = delete_account('testuser', DB_PATH)
        
        assert result == {
            "success": True,
            "message": "Account deleted successfully.",
        }

def test_delete_account_username_does_not_exist():
    dummy_users = {}
    with patch('server.account_management.load_user_data', return_value=dummy_users):
        
        result = delete_account('nonexistentuser', DB_PATH)
        
        assert result == {
            "success": False,
            "message": "Username does not exist.",
        }

def test_delete_account_offline_user():
    dummy_users = {
        'testuser': {
            'username': 'testuser',
            'password': 'hashed_password',
            'online': False
        }
    }
    with patch('server.account_management.load_user_data', return_value=dummy_users), \
         patch('server.account_management.save_user_data') as mock_save, \
         patch('builtins.open', mock_open()), \
         patch('os.path.exists', return_value=True):
        result = delete_account('testuser', DB_PATH)
        assert result == {
            "success": False,
            "message": "Attempting to delete offline account.",
        }