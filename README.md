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
Upon running ```driver.py``` and ```ui.py```, the GUI will then pop up with an initial login/signup page where the user can input a username or password and then click either login or signup. Once logged in, a new "starting" screen will pop up with a main text box, and buttons corresponding to actions the user can do. 

Upon clicking the send message button, the user will be taken to a new screen and there they can enter a target username they want to receive their message, and then the message they would like to send. The user can then hit send to send the message, or they can press the back button taking them back to the starting screen.

When clicking the list users button, the user will be taken to a screen where they can input a username pattern and press a button to list the users matching the pattern, and then those users are displayed in the text box. The user can press the back button to return to the starting screen. 

When clicking the read messages button, the user is taken to a screen where they can input how many messages they want to read from their unread messages. The messages are then displayed to the user. The user can also press the back button to return to the previous screen.

Clicking the delete message button will take the user to a screen which displays all messages that user has sent which have not been read by the receiver yet. The user is then prompted to enter the message_id of the message they want to delete. They can then hit delete to delete the specified message, or press back at any time to return to the starting screen. 

The logout and delete account button upon being clicked will close the GUI and accordingly log the user out or delete the user’s account. 

For any of these requests, there may be a slight delay of a few seconds if the request is sent in the middle of the servers conducting leader elections, so please be patient if a request does not immediately process!

# Additional Documentation
Additional documentation for this project can be found here: [https://docs.google.com/document/d/1YmHQOeT9xTAVMLlScoJI2uOaV_kc11jniBPDSLFM9VE/edit?tab=t.0](https://docs.google.com/document/d/1YmHQOeT9xTAVMLlScoJI2uOaV_kc11jniBPDSLFM9VE/edit?tab=t.0)

# Running Tests
To run our test suite, cd into the tests folder and run ```pytest``` in the terminal.
