import json 
import os 
import re
import time
import uuid
import bcrypt
import shutil

USER_DATA_FILE = "user_data.json"

def load_user_data(db_path):
    # user_data_path = get_user_data_pathname()
    user_data_path = os.path.join(db_path, USER_DATA_FILE)

    if os.path.exists(user_data_path):
        with open(user_data_path, "r") as f:
            return json.load(f)
    return {}

def save_user_data(users, db_path):
    # user_data_path = get_user_data_pathname()
    user_data_path = os.path.join(db_path, USER_DATA_FILE)
    with open(user_data_path, "w") as f:
        json.dump(users, f)


def username_exists(username, db_path):
    existing_users = load_user_data(db_path)

    return username in existing_users

def create_account(username, password, db_path): 
    existing_users = load_user_data(db_path)

    if not username or not password:
        return {
            "success": False, 
            "message": "Username and/or password cannot be empty."
        }
    if username_exists(username, db_path):
        return {
            "success": False, 
            "message": "Username already exists. Please try again.",
        }
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    existing_users[username] = {
        "username": username, 
        "password": hashed_password.decode('utf-8'), 
        "online": True, 
    }

    save_user_data(existing_users, db_path)

    # db_pathname = get_db_pathname()
    user_file_path = os.path.join(db_path, "unread_messages", f"{username}.json")
    with open(user_file_path, 'w') as user_file:
        json.dump([], user_file)
    return {
        "success": True, "message": 
        "Account created successfully.",
    }

def login(username, password, db_path):
    existing_users = load_user_data(db_path)
    is_online = check_if_online(username, db_path)
    if is_online:
        return {
            "success": False, 
            "message": "User is already logged in.",
        }
    if username_exists(username, db_path):
        user = existing_users[username]
        if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            user["online"] = True
            save_user_data(existing_users, db_path)

            # Get number of unread messages
            unread_messages_path = os.path.join(db_path, "unread_messages", f"{username}.json")
            unread_message_count = 0
            if os.path.exists(unread_messages_path):
                with open(unread_messages_path, "r") as f:
                    unread_messages = json.load(f)
                    unread_message_count = len(unread_messages)
            
            return {
                "success": True, 
                "message": "Login successful.",
                "unread_message_count": unread_message_count
            }
      
    return {
        "success": False, 
        "message": "Incorrect username or password. Please try again.",
    }

def logout(username, db_path):
    existing_users = load_user_data(db_path)

    if not username_exists(username, db_path):
        return {
            "success": False, 
            "message": "Username does not exist.",
        }

    user = existing_users[username]
    user["online"] = False

    save_user_data(existing_users, db_path)
    return {
        "success": True, 
        "message": "Logout successful.",
    }
   

def list_accounts(username_pattern, db_path):
    try:
        existing_users = load_user_data(db_path)
        matching_users = [username for username in existing_users.keys() if re.search(username_pattern, username)]
        return {
            "success": True, 
            "message": "Accounts listed successfully.", 
            "matches": matching_users,
            }
    except re.PatternError:
        return {
            "success": False, 
            "message": "Invalid regex pattern.",
        }

def send_offline_message(target_username, sender_username, message, timestamp, db_path, message_id=None):
    '''
        Sends an offline message to the target user. Returns a response to be 
        sent back to the client and the message ID.
    '''

    # Generate a unique message ID
    if not message_id:
        message_id = str(uuid.uuid4())

    # Find path to target user's unread messages
    target_db_pathname = os.path.join(db_path, "unread_messages", f"{target_username}.json")

    if not os.path.exists(target_db_pathname) or not username_exists(target_username, db_path):
        res = {
            "success": False,
            "message": "Target user does not exist.",
        }
        return res, -1

    new_message = {"message_id": message_id, "message": message, "sender": sender_username, "timestamp": timestamp}
    with open(target_db_pathname, "r") as f:
        unread_messages = json.load(f)
    
    # Find the position to insert the new message to maintain sorted time order
    insert_position = len(unread_messages)
    for i in range(len(unread_messages) - 1, -1, -1):
        if unread_messages[i]["timestamp"] <= timestamp:
            insert_position = i + 1
            break

    # Insert the new message at the correct position
    unread_messages.insert(insert_position, new_message)
    with open(target_db_pathname, "w") as f:
        json.dump(unread_messages, f)

    # Save the sent message to the sender's sent messages
    sent_db_pathname = os.path.join(db_path, "sent_messages", f"{sender_username}.json")
    if not os.path.exists(sent_db_pathname):
        sent_messages = {}
    else:
        with open(sent_db_pathname, "r") as f:
            sent_messages = json.load(f)
    
    if target_username not in sent_messages:
        sent_messages[target_username] = []
    
    sent_messages[target_username].append(new_message)
    with open(sent_db_pathname, "w") as f:
        json.dump(sent_messages, f)

    res = {
        "success": True, 
        "message": "Message sent successfully.",
    }
    return res, message_id

def read_messages(username, num_messages, db_path):
    # db_pathname = get_db_pathname()

    # Find path to target user's unread messages
    target_db_pathname = os.path.join(db_path, "unread_messages", f"{username}.json")
    if not os.path.exists(target_db_pathname):
        return {
            "success": False, 
            "message": "Target user does not exist.",
        }

    with open(target_db_pathname, "r") as f:
        unread_messages = json.load(f)

    msg_to_read = unread_messages[:num_messages]
    
    with open(target_db_pathname, "w") as f:
        json.dump(unread_messages[num_messages:], f)

    for message in msg_to_read: 
        sender_username = message["sender"]
        message_id = message["message_id"]
        sent_db_pathname = os.path.join(db_path, "sent_messages", f"{sender_username}.json")
        if os.path.exists(sent_db_pathname):
            with open(sent_db_pathname, "r") as f:
                sent_messages = json.load(f)
            for recipient, messages in sent_messages.items():
                sent_messages[recipient] = [msg for msg in messages if msg["message_id"] != message_id]
            with open(sent_db_pathname, "w") as f:
                json.dump(sent_messages, f)
                
    return_data = {
        "success": True,
        "message": "Messages read successfully.",
        "messages": unread_messages[:num_messages],
    }
    return return_data

def check_if_online(username, db_path):
    existing_users = load_user_data(db_path)
    if username in existing_users:
        user = existing_users[username]
        return user["online"]
    
    return False

def logout_all_users(db_path):
    existing_users = load_user_data(db_path)
    for username in existing_users:
        user = existing_users[username]
        user["online"] = False
        user["host"] = ""
        user["port"] = ""
    save_user_data(existing_users, db_path)

def delete_account(username, db_path):
    existing_users = load_user_data(db_path)

    if username not in existing_users:
        return {
            "success": False, 
            "message": "Username does not exist.",
        }
    
    if existing_users[username]["online"]:
        del existing_users[username]
        save_user_data(existing_users, db_path)

        # db_pathname = get_db_pathname()
        unread_messages_path = os.path.join(db_path, "unread_messages", f"{username}.json")
        if os.path.exists(unread_messages_path):
            os.remove(unread_messages_path)

        sent_messages_path = os.path.join(db_path, "sent_messages", f"{username}.json")
        if os.path.exists(sent_messages_path):
            os.remove(sent_messages_path)

        return {
            "success": True, 
            "message": "Account deleted successfully.",
        }
    
    return {
        "success": False, 
        "message": "Attempting to delete offline account.",
    }
    
def delete_message(username, message_id, db_path):
    # db_pathname = get_db_pathname()

    # Load the user's sent messages
    sent_db_pathname = os.path.join(db_path, "sent_messages", f"{username}.json")
    if not os.path.exists(sent_db_pathname):
        return {"success": False, "message": "No sent messages found."}
    
    with open(sent_db_pathname, "r") as f:
        sent_messages = json.load(f)
    
    # Find and delete the message with the given message_id
    target_username = None
    for recipient, messages in sent_messages.items():
        for message in messages: 
            if message["message_id"] == message_id:
                target_username = recipient
                break
        if target_username:
            break

    if not target_username: 
        return {"success": False, "message": "Message ID not found."}
    
    # Remove message from sent_messages
    sent_messages[target_username] = [msg for msg in sent_messages[target_username] if msg["message_id"] != message_id]
    with open(sent_db_pathname, "w") as f:
        json.dump(sent_messages, f)

    # Load the target user's unread messages
    target_db_pathname = os.path.join(db_path, "unread_messages", f"{target_username}.json")
    if not os.path.exists(target_db_pathname):
        return {"success": False, "message": "Target user does not exist."}
    with open(target_db_pathname, "r") as f:
        unread_messages = json.load(f)

    # Remove message from target user's unread_messages
    unread_messages = [msg for msg in unread_messages if msg["message_id"] != message_id]
    with open(target_db_pathname, "w") as f:
        json.dump(unread_messages, f)

    return {"success": True, "message": "Message deleted successfully."}


def fetch_sent_messages(username, db_path):
    # db_pathname = get_db_pathname()
    sent_db_pathname = os.path.join(db_path, "sent_messages", f"{username}.json")
    if not os.path.exists(sent_db_pathname):
        return {"success": False, "message": "No sent messages found."}

    with open(sent_db_pathname, "r") as f:
        sent_messages = json.load(f)
    return {"success": True, "message": "Sent messages fetched successfully.", "sent_messages": sent_messages}

def upload_image(username, image_name, file_type, album_name, db_path, image_data):
    """
    Uploads an image for the user. The image is saved in a directory structure based on the username, 
    file type, and album name.
    """
    if not username or not image_name or not file_type or not album_name:
        return {"success": False, "message": "Username, image name, file type, and album cannot be empty."}

    if file_type.lower() not in ["jpg", "jpeg", "png"]:
        return {"success": False, "message": "Unsupported file type. Supported types are: jpg, jpeg, png, gif."}


    album_dir = os.path.join(db_path, "albums", album_name)

    if not os.path.exists(album_dir):
        # os.makedirs(album_dir)
        return {"success": False, "message": "Album does not exist"}

    # Check if the user has permission to upload to the album
    album_metadata_path = os.path.join(album_dir, "metadata.json")
    if os.path.exists(album_metadata_path):
        with open(album_metadata_path, "r") as f:
            album_metadata = json.load(f)
    else:
        return {"success": False, "message": "Album metadata file not found."}
    
    if username not in album_metadata["editors"]:
        return {"success": False, "message": "You do not have permission to upload to this album."}
    
    image_dir = os.path.join(album_dir, image_name)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Create metadata file for the image
    metadata = {
        "username": username,
        "image_name": image_name,
        "file_type": file_type,
        "timestamp": time.time(),
    }

    metadata_path = os.path.join(image_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)
    
    # Save the image file
    image_path = os.path.join(image_dir, f"{image_name}.{file_type}")
    
    # Check if the image already exists
    if os.path.exists(image_path):
        return {"success": False, "message": "Image already exists."}

    # Save the image 
    with open(image_path, 'wb') as f:
        f.write(image_data)

    return {"success": True, "message": "Image uploaded successfully."}

def create_album(username, album_name, db_path):
    """
    Creates an album for the user. The album is saved in a directory structure based on the username.
    """
    if not username or not album_name:
        return {"success": False, "message": "Username and album name cannot be empty."}

    user_album_dir = os.path.join(db_path, "albums", album_name)

    if os.path.exists(user_album_dir):
        return {"success": False, "message": "Album with given name already exists."}

    os.makedirs(user_album_dir)

    # Create metadata file for the album
    metadata = {
        "creator": username,
        "album_name": album_name,
        "timestamp": time.time(),
        "editors": [username],
    }
    metadata_path = os.path.join(user_album_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)
    
    # Update user profile with newly created album
    existing_users = load_user_data(db_path)
    existing_users[username]["albums"].append(album_name)
    save_user_data(existing_users, db_path)

    return {"success": True, "message": "Album created successfully."}

def add_album_editor(requestor_username, editor_username, album_name, db_path):
    album_dir = os.path.join(db_path, "albums", album_name)
    if not os.path.exists(album_dir):
        return {"success": False, "message": "Album does not exist."}
    
    existing_users = load_user_data(db_path)
    if editor_username not in existing_users:
        return {"success": False, "message": "Editor username does not exist."}
    
    # Check if the requestor is the creator of the album
    metadata_path = os.path.join(album_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        return {"success": False, "message": "Album metadata file not found."}
    with open(metadata_path, "r") as f:
        album_metadata = json.load(f)

    if requestor_username not in album_metadata["editors"]:
        return {"success": False, "message": "You do not have permission to add editors to this album."}

    if editor_username in album_metadata["editors"]:
        return {"success": False, "message": "Editor already exists in the album."}
    
    album_metadata["editors"].append(editor_username)
    with open(metadata_path, "w") as f:
        json.dump(album_metadata, f)

    # Update the user's profile to include the album
    existing_users[editor_username]["albums"].append(album_name)
    save_user_data(existing_users, db_path)

    return {"success": True, "message": f"{editor_username} added as editor to {album_name}."}

def remove_album_editor(requestor_username, editor_username, album_name, db_path):
    album_dir = os.path.join(db_path, "albums", album_name)
    if not os.path.exists(album_dir):
        return {"success": False, "message": "Album does not exist."}
    
    existing_users = load_user_data(db_path)
    if editor_username not in existing_users:
        return {"success": False, "message": "Editor username does not exist."}
    
    # Check if the requestor is the creator of the album
    metadata_path = os.path.join(album_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        return {"success": False, "message": "Album metadata file not found."}
    with open(metadata_path, "r") as f:
        album_metadata = json.load(f)

    if editor_username == album_metadata["creator"]:
        return {"success": False, "message": "Cannot remove the creator of the album."}
    
    if requestor_username not in album_metadata["editors"]:
        return {"success": False, "message": "You do not have permission to remove editors to this album."}

    if editor_username not in album_metadata["editors"]:
        return {"success": False, "message": "The person you are trying to remove does not have access to the album."}
    
    album_metadata["editors"].remove(editor_username)
    with open(metadata_path, "w") as f:
        json.dump(album_metadata, f)

    # Update the user's profile to include the album
    existing_users[editor_username]["albums"].remove(album_name)
    save_user_data(existing_users, db_path)

    return {"success": True, "message": f"{editor_username} removed as editor from {album_name}."}

def delete_album(username, album_name, db_path):
    """
    Deletes an album for the user. The album is deleted from the directory structure based on the username.
    """
    if not username or not album_name:
        return {"success": False, "message": "Username and album name cannot be empty."}

    album_dir = os.path.join(db_path, "albums", album_name)

    if not os.path.exists(album_dir):
        return {"success": False, "message": "Album does not exist."}

    # Check if the user is the creator of the album
    metadata_path = os.path.join(album_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        return {"success": False, "message": "Album metadata file not found."}
    
    with open(metadata_path, "r") as f:
        album_metadata = json.load(f)

    if album_metadata["creator"] != username:
        return {"success": False, "message": "You do not have permission to delete this album."}

    # Delete the album directory
    shutil.rmtree(album_dir)

    # Update user profile to remove the deleted album
    existing_users = load_user_data(db_path)
    existing_users[username]["albums"].remove(album_name)
    save_user_data(existing_users, db_path)

    return {"success": True, "message": "Album deleted successfully."}

def delete_image(username, image_name, album_name, db_path):
    '''
        Deletes an image from an album
    '''
    if not username or not album_name:
        return {"success": False, "message": "Username and album name cannot be empty."}

    album_dir = os.path.join(db_path, "albums", album_name)

    if not os.path.exists(album_dir):
        return {"success": False, "message": "Album does not exist."}

    # Check if the user is editor of the album
    metadata_path = os.path.join(album_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        return {"success": False, "message": "Album metadata file not found."}
    with open(metadata_path, "r") as f:
        album_metadata = json.load(f)
    if username not in album_metadata["editors"]:
        return {"success": False, "message": "You do not have permission to delete images from this album."}
    
    image_dir = os.path.join(album_dir, image_name)
    if not os.path.exists(image_dir):
        return {"success": False, "message": "Image does not exist."}
    image_metadata_path = os.path.join(image_dir, "metadata.json")
    with open(image_metadata_path, "r") as f:
        image_metadata = json.load(f)

    if image_metadata["username"] != username:
        return {"success": False, "message": "You do not have permission to delete this image because you are not the initial image creator."}
    
    # Delete the image directory
    shutil.rmtree(image_dir)
    return {"success": True, "message": "Image deleted successfully."}

def fetch_photos(username, album_name, page, page_size, db_path):
    '''
        Fetches photos from an album. Returns a list of photos with pagination.
    '''
    if not username or not album_name:
        return {"success": False, "message": "Username and album name cannot be empty."}

    album_dir = os.path.join(db_path, "albums", album_name)

    if not os.path.exists(album_dir):
        return {"success": False, "message": "Album does not exist."}

    # Check if the user is editor of the album
    metadata_path = os.path.join(album_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        return {"success": False, "message": "Album metadata file not found."}
    with open(metadata_path, "r") as f:
        album_metadata = json.load(f)
    if username not in album_metadata["editors"]:
        return {"success": False, "message": "You do not have permission to fetch images from this album."}

    # Fetch all images in the album
    images = []
    for root, dirs, files in os.walk(album_dir):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_path = os.path.join(root, file)
                metadata_path = os.path.join(root, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    images.append({
                        "image_path": image_path,
                        "metadata": metadata,
                    })

    # Sort images by timestamp
    images.sort(key=lambda x: x["metadata"]["timestamp"])

    # Implement pagination
    start_index = (page) * page_size
    if start_index >= len(images):
        return {"success": False, "message": "No more images to display."}
    
    end_index = min(start_index + page_size, len(images))
    paginated_images = images[start_index:end_index]
    return {
        "success": True, 
        "message": "Images fetched successfully.", 
        "images": paginated_images,
    }


def get_db_pathname():
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.dirname(current_dir)
    db_pathname = os.path.join(base_dir, 'db')
    return db_pathname

def get_user_data_pathname():
    db_pathname = get_db_pathname()
    user_data_pathname = os.path.join(db_pathname, USER_DATA_FILE)
    return user_data_pathname

    
