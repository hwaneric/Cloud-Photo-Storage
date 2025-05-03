import json 
import os 
import re
import time
import uuid
import bcrypt
import shutil
import stat

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
        "albums": []  # Initialize empty albums list for new user
    }

    save_user_data(existing_users, db_path)
    return {
        "success": True, 
        "message": "Account created successfully."
    }

def login(username, password, db_path):
    existing_users = load_user_data(db_path)
    is_online = check_if_online(username, db_path)
    if is_online:
        return {
            "success": False, 
            "message": "User is already logged in."
        }
    if username_exists(username, db_path):
        user = existing_users[username]
        if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            user["online"] = True
            save_user_data(existing_users, db_path)
            return {
                "success": True, 
                "message": "Login successful."
            }
      
    return {
        "success": False, 
        "message": "Incorrect username or password. Please try again."
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
            "message": "Username does not exist."
        }
    
    if not existing_users[username].get("online", False):
        return {
            "success": False,
            "message": "Attempting to delete offline account.",
        }
    
    user_albums = existing_users[username].get("albums", [])
    for album_name in user_albums:
        album_dir = os.path.join(db_path, "albums", album_name)
        metadata_path = os.path.join(album_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            continue
        with open(metadata_path, "r") as f:
            album_metadata = json.load(f)
        if album_metadata["creator"] == username:
            # User is creator: delete the whole album
            try:
                shutil.rmtree(album_dir, onerror=on_rm_error)
            except Exception:
                pass
            # Remove this album from all users' album lists
            for other_user in existing_users:
                if album_name in existing_users[other_user].get("albums", []):
                    existing_users[other_user]["albums"].remove(album_name)
        else:
            # User is just an editor: remove their images and remove from editors list
            # Remove user's images
            for image_folder in os.listdir(album_dir):
                image_dir = os.path.join(album_dir, image_folder)
                if os.path.isdir(image_dir):
                    image_metadata_path = os.path.join(image_dir, "metadata.json")
                    if os.path.exists(image_metadata_path):
                        with open(image_metadata_path, "r") as f:
                            image_metadata = json.load(f)
                        if image_metadata.get("username") == username:
                            try:
                                shutil.rmtree(image_dir, onerror=on_rm_error)
                            except Exception:
                                pass
            # Remove user from editors list
            if username in album_metadata["editors"]:
                album_metadata["editors"].remove(username)
                with open(metadata_path, "w") as f:
                    json.dump(album_metadata, f)
    # Remove user from user_data
    del existing_users[username]
    save_user_data(existing_users, db_path)
    return {"success": True, "message": "Account deleted successfully."}

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
    
    # Remove file extension from the image name if it exists
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_name = os.path.splitext(image_name)[0]

    # Save the image file
    image_path = os.path.join(image_dir, f"{image_name}.{file_type}")
    
    # Check if the image already exists
    if os.path.exists(image_path):
        return {"success": False, "message": "Image already exists."}

    # Save the image 
    with open(image_path, 'wb') as f:
        f.write(image_data)

    return {"success": True, "message": "Image uploaded successfully.", "image_path": image_path}

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

def on_rm_error(func, path, exc_info):
    # Remove read-only attribute and retry
    os.chmod(path, stat.S_IWRITE)
    func(path)

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

    # Delete the album directory with robust error handling
    try:
        shutil.rmtree(album_dir, onerror=on_rm_error)
    except Exception as e:
        return {"success": False, "message": f"Failed to delete album directory: {e}"}

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
        return {"success": True, "message": "Image already deleted."}
    image_metadata_path = os.path.join(image_dir, "metadata.json")
    if not os.path.exists(image_metadata_path):
        # If the metadata is missing, treat as already deleted
        try:
            shutil.rmtree(image_dir, onerror=on_rm_error)
        except Exception:
            pass
        return {"success": True, "message": "Image already deleted or metadata missing."}
    with open(image_metadata_path, "r") as f:
        image_metadata = json.load(f)

    if image_metadata["username"] != username:
        return {"success": False, "message": "You do not have permission to delete this image because you are not the initial image creator."}
    
    # Delete the image directory with robust error handling
    try:
        shutil.rmtree(image_dir, onerror=on_rm_error)
    except Exception as e:
        return {"success": False, "message": f"Failed to delete image directory: {e}"}
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

def fetch_albums(username, db_path): 
    '''
        Fetches all albums for a user.
    '''
    if not username:
        return {"success": False, "message": "Username cannot be empty."}
    users = load_user_data(db_path)

    if username not in users:
        return {"success": False, "message": "User does not exist."}
    
    user_albums = users[username].get("albums", [])
    return {
        "success": True, 
        "message": "Albums fetched successfully.", 
        "albums": user_albums,
    }   

def fetch_album_editors(username, album_name, db_path):
    '''
        Fetches all editors for an album.
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
        return {"success": False, "message": "You do not have permission to fetch editors from this album."}

    return {
        "success": True, 
        "message": "Editors fetched successfully.", 
        "editors": album_metadata["editors"],
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

    
