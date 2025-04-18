import tkinter as tk
from tkinter import messagebox
from client import Client
import threading
from dotenv import load_dotenv
import os

load_dotenv(override=True)
SERVER_HOST = os.getenv("SERVER_HOST_0")
SERVER_PORT = int(os.getenv("SERVER_PORT_0"))
CLIENT_HOST = os.getenv("CLIENT_HOST")

class ChatApp: 
    def __init__(self, root, client):
        self.client = client
        self.root = root 
        self.root.title("Chat Application")

        self.login_frame = tk.Frame(self.root)
        self.chat_frame = tk.Frame(self.root)
        self.message_frame = tk.Frame(self.root)
        self.list_frame = tk.Frame(self.root)
        self.read_frame = tk.Frame(self.root)
        self.delete_message_frame = tk.Frame(self.root)

        self.create_login_frame()
        self.create_chat_frame()
        self.create_message_frame()
        self.create_list_frame()
        self.create_read_frame()
        self.create_delete_message_frame()

        self.login_frame.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_login_frame(self):
        tk.Label(self.login_frame, text="Username").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)
        
        tk.Label(self.login_frame, text="Password").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)
        
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2)
        
        self.signup_button = tk.Button(self.login_frame, text="Signup", command=self.signup)
        self.signup_button.grid(row=3, column=0, columnspan=2)
    
    def create_chat_frame(self): 
        self.incoming_message_list = tk.Listbox(self.chat_frame, height=15, width=50)
        self.incoming_message_list.pack()

        self.send_button = tk.Button(self.chat_frame, text="Send Message", command=self.show_message_frame)
        self.send_button.pack()
        
        self.list_button = tk.Button(self.chat_frame, text="List Users", command=self.show_list_frame)
        self.list_button.pack()

        self.read_button = tk.Button(self.chat_frame, text="Read Messages", command=self.show_read_frame)
        self.read_button.pack()

        self.delete_message_button = tk.Button(self.chat_frame, text="Delete Message", command=self.show_delete_message_frame)
        self.delete_message_button.pack()
        
        self.logout_button = tk.Button(self.chat_frame, text="Logout", command=self.logout)
        self.logout_button.pack()

        self.delete_account_button = tk.Button(self.chat_frame, text="Delete Account", command=self.delete_account) 
        self.delete_account_button.pack()
    
    def create_message_frame(self):        
        tk.Label(self.message_frame, text="Target Username").pack()
        self.target_username_entry = tk.Entry(self.message_frame, width=50)
        self.target_username_entry.pack()
        
        tk.Label(self.message_frame, text="Message").pack()
        self.message_entry = tk.Entry(self.message_frame, width=50)
        self.message_entry.pack()
        
        self.send_message_button = tk.Button(self.message_frame, text="Send", command=self.message)
        self.send_message_button.pack()
        
        self.back_button = tk.Button(self.message_frame, text="Back", command=self.show_chat_frame)
        self.back_button.pack()

    def create_list_frame(self):
        self.list_message = tk.Listbox(self.list_frame, height=15, width=50)
        self.list_message.pack()

        tk.Label(self.list_frame, text="Username Pattern").pack()
        self.username_pattern_entry = tk.Entry(self.list_frame, width=50)
        self.username_pattern_entry.pack()
        
        self.list_users_button = tk.Button(self.list_frame, text="List Users", command=self.list)
        self.list_users_button.pack()
        
        self.back_button = tk.Button(self.list_frame, text="Back", command=self.show_chat_frame)
        self.back_button.pack()

    def create_read_frame(self):
        self.read_message_list = tk.Listbox(self.read_frame, height=15, width=50)
        self.read_message_list.pack()

        tk.Label(self.read_frame, text="Number of Messages").pack()
        self.num_messages_entry = tk.Entry(self.read_frame, width=50)
        self.num_messages_entry.pack()
        
        self.read_messages_button = tk.Button(self.read_frame, text="Read Messages", command=self.read)
        self.read_messages_button.pack()
        
        self.back_button = tk.Button(self.read_frame, text="Back", command=self.show_chat_frame)
        self.back_button.pack()

    def create_delete_message_frame(self):
        self.delete_message_list = tk.Listbox(self.delete_message_frame, height=15, width=50)
        self.delete_message_list.pack()

        tk.Label(self.delete_message_frame, text="Message ID to Delete").pack()
        self.delete_messages_entry = tk.Entry(self.delete_message_frame, width=50)
        self.delete_messages_entry.pack()

        self.delete_message_button = tk.Button(self.delete_message_frame, text="Delete Message", command=self.delete_message)
        self.delete_message_button.pack()

        self.back_button = tk.Button(self.delete_message_frame, text="Back", command=self.show_chat_frame)
        self.back_button.pack()
    
    def show_chat_frame(self):
        self.message_frame.pack_forget()
        self.list_frame.pack_forget()
        self.read_frame.pack_forget()
        self.delete_message_frame.pack_forget()
        self.chat_frame.pack()
    
    def show_message_frame(self):
        self.chat_frame.pack_forget()
        self.message_frame.pack()
    
    def show_list_frame(self):
        self.chat_frame.pack_forget()
        self.list_frame.pack()

    def show_read_frame(self):
        self.chat_frame.pack_forget()
        self.read_frame.pack()

    def show_delete_message_frame(self):
        self.chat_frame.pack_forget()
        self.fetch_sent_messages()
        self.delete_message_frame.pack()

    def update_incoming_messages(self, message):
        self.incoming_message_list.insert(tk.END, message)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message, unread_message_count = self.client.login(username, password)
        if success:
            print("message", message)
            messagebox.showinfo("Login Successful", message)  
            self.login_frame.pack_forget()
            self.chat_frame.pack()
            self.incoming_message_list.delete(0, tk.END)
            self.incoming_message_list.insert(tk.END, f"Welcome {username}! On initial log in, you had {unread_message_count} unread messages.")
            threading.Thread(target=self.client.listen_for_messages, args=(self.update_incoming_messages,), daemon = True).start()
        else: 
            messagebox.showerror("Login Failed", message)

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.client.signup(username, password)
        if success:
            messagebox.showinfo("Signup Successful", message)
            self.login_frame.pack_forget()
            self.chat_frame.pack()
            threading.Thread(target=self.client.listen_for_messages, args=(self.update_incoming_messages,), daemon = True).start()
        else: 
            messagebox.showerror("Signup Failed", message)
    
    def message(self):
        target_username = self.target_username_entry.get()
        message = self.message_entry.get()
        success, response = self.client.message(target_username, message)
        if success:
            messagebox.showinfo("Message Sent", response)
        else:
            messagebox.showerror("Message Failed", response)

    def list(self):
        username_pattern = self.username_pattern_entry.get()
        success, response = self.client.list(username_pattern)
        if success:
            self.list_message.insert(tk.END, "User List:")
            for user in response:
                self.list_message.insert(tk.END, user)
        else:
            messagebox.showerror("List Users Failed", response)
    
    def read(self):
        num_messages = self.num_messages_entry.get()
        if not num_messages.isdigit():
            messagebox.showerror("Invalid Input", "Number of messages must be an integer")
            return
        num_messages = int(num_messages)
        success, response = self.client.read(num_messages)
        if success:
            if not response:
                messagebox.showinfo("No Messages", "You have no unread messages")
                return
            self.read_message_list.delete(0, tk.END)
            for message in response:
                self.read_message_list.insert(tk.END, message)
        else:
            messagebox.showerror("Read Messages Failed", response)

    def fetch_sent_messages(self):
        success, response = self.client.fetch_sent_messages()
        if success:
            self.delete_message_list.delete(0, tk.END)
            for recipient, messages in response.items():
                for message in messages:
                    display_message = f"To: {recipient}, ID: {message['message_id']}, Message: {message['message']}"
                    self.delete_message_list.insert(tk.END, display_message)
        else:
            messagebox.showerror("Fetch Sent Messages Failed", response)

    def delete_message(self):
        message_id = self.delete_messages_entry.get()
        if not message_id:
            messagebox.showerror("Invalid Input", "Message ID cannot be empty")
            return
        success, response = self.client.delete_message(message_id)
        if success:
            messagebox.showinfo("Delete Message Successful", response)
            self.fetch_sent_messages()
        else:
            messagebox.showerror("Delete Message Failed", response)

    def logout(self):
        if not self.client.username:
            return False, "You are not logged in! Logout unsuccessful"
        success, response = self.client.logout()
        if success:
            messagebox.showinfo("Logout Successful", response)
            self.root.destroy()
        else: 
            messagebox.showerror("Logout Failed", response)

    def delete_account(self):
        if not self.client.username:
            return False, "You are not logged in! Delete account unsuccessful"
        success, response = self.client.delete_account()
        if success:
            messagebox.showinfo("Delete Account Successful", response)
            self.root.destroy()
        else:
            messagebox.showerror("Delete Account Failed", response)

    def on_closing(self):
        if self.client.username: 
            self.client.logout()
        self.root.destroy()


if __name__ == "__main__":
    try:
        print("CLIENT HOST:", CLIENT_HOST)
        client = Client(SERVER_HOST, SERVER_PORT, CLIENT_HOST)
        root = tk.Tk()
        app = ChatApp(root, client)
        root.mainloop()
    except KeyboardInterrupt:
        print("Client interrupted by user, exiting...")
    finally:
        if client.username:
            client.logout()
