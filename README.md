# Overview
A cloud-based photo storage system that you can run on your own machines! The system is 2-fault tolerant and supports creating shared albums with other users

# Getting Started Locally
To start running our project locally, first create a Python virtual environment in the root directory by running ```python -m venv venv```. Then activate the venv by running the OS appropriate script as noted in this article: https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/#

Once the venv is active, download the project requirements by running ```pip3 install -r requirements.txt```.

Next, make sure Tkinter is downloaded. Tkinter may not download via pip3, so it may be necessary to install it separately using a tool like Homebrew. On Mac, make sure you have homebrew downloaded and run ```brew install python-tk``` to download Tkinter if necessary.

Also in the root directory, create a .env file, which is where we store sensitive configuration details. You will need the following configuration variables:
```
SERVER_HOST_0 = "{SERVER 0 HOST HERE}"
SERVER_PORT_0 = {SERVER 0 PORT HERE}
SERVER_HOST_1 = "{SERVER 1 HOST HERE}"
SERVER_PORT_1 = {SERVER 1 PORT HERE}
SERVER_HOST_2 = "{SERVER 2 HOST HERE}"
SERVER_PORT_2 = {SERVER 2 PORT HERE}
```
The server hosts and ports should be the hosts and ports that the corresponding server is accessible from. If running on multiple machines, make sure that all the hosts are actual IP addresses and not "localhost" or any equivalents.

Once the above configuration steps are complete, you should be able to run the project! 
To run the servers, cd into the server folder and run ```python3 driver.py <server_id> <optional: db_path>```. This will begin running one of the servers, so run the command in 3 separate terminal sessions to run all 3 servers simultaneously. The server id is the id of the server you would like to run (must either be 0, 1, or 2). The optional db_path parameter allows the user to specify a custom path to the database file for the server, <b> however we recommend not using the optional db_path parameter unless there is a very strong, specific reason for doing so.</b> If a db_path is not provided, the servers will default to server 0 using the db_0 file, server 1 using the db_1 file, and server 2 using the db_2 file. 

To run the client, cd into the client folder and run ```ui.py```.

# Using the GUI
Upon running ```driver.py``` and ```ui.py```, the GUI will then pop up with an initial login/signup page where the user can input a username or password and then click either login or signup. Once logged in, the "main" screen will pop up. The main screen consists of buttons corresponding to actions that the user can perform.

Upon clicking the create album button, the user will be taken to a new screen where they can enter an album name and any users they want as editors for the created album. On the page, all users are listed for the client's reference. Once filled in, the user can then hit create album, or if they change their mind they can press the back button to go back to the main screen. 

When clicking the upload photos button, the user is taken to a new screen where the albums that they have permission to upload to are listed. The user can select one of those albums and then click the upload photo button. Upon clicking this, the user's files will be opened and they can select a photo/image to be uploaded to the server. Finally, for the user to go back to the main screen they can simply click the back button. 

The user can also click a view album button on the main screen, taking them to a new page for viewing photos. The left side of this page displays a list of available albums. When an album is selected, its photos appear on the right side of the screen. Users can select any photo to preview it on a canvas located just above the photo list. Clicking the canvas enlarges the selected photo in a pop-up window for a focused, full-screen view. Beneath the photo thumbnails, "Previous" and "Next" buttons allow users to browse through the album in a paginated format. The users can also hit the back button to return to the main screen. 

When clicking the delete album button, the user is taken to a new screen where the albums they have access to are listed. The user can then select one of these albums and click the delete button to try to delete the album. Depending on if they were the creator or not, they will be met accordingly with a "success" or "failure" message. The user can also press the back button to go back to the main page. 

Clicking on the edit album privileges button takes the user to a page where their albums are listed on the lefthand side. Upon selecting an album, the right-hand side updates to display the current editors at the top, followed by a list of users who are not yet editors. Users can manage editor permissions by selecting names from either list or by manually entering usernames. They can then use the "Add Editor" or "Remove Selected Editor" buttons to modify editing access accordingly. The user can then go back to the main page by clicking the back button. 

The user can additionally click on the delete images button, which takes them to a page where the albums they are a part of are listed on the left-hand side. Once an album is selected, the images that the user can delete are then listed on the right-hand side. The user can then select an image and click the delete selected image button to delete it. To go back to the main screen the user can simply click the back button. 

The logout and delete account button upon being clicked will close the GUI and accordingly log the user out or delete the user’s account. 

For any of these requests, there may be a slight delay of a few seconds if the request is sent in the middle of the servers conducting leader elections, so please be patient if a request does not immediately process!

# Additional Documentation
Additional documentation for this project can be found here: [https://docs.google.com/document/d/1YmHQOeT9xTAVMLlScoJI2uOaV_kc11jniBPDSLFM9VE/edit?tab=t.0](https://docs.google.com/document/d/1YmHQOeT9xTAVMLlScoJI2uOaV_kc11jniBPDSLFM9VE/edit?tab=t.0)

# Running Tests
To run our test suite, cd into the tests folder and run ```pytest``` in the terminal.
