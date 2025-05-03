import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from client import Client
import threading
from dotenv import load_dotenv
import os
from PIL import Image, ImageTk
import io

load_dotenv(override=True)
SERVER_HOST = os.getenv("SERVER_HOST_0")
SERVER_PORT = int(os.getenv("SERVER_PORT_0"))
CLIENT_HOST = os.getenv("CLIENT_HOST")

class PhotoApp:
    def __init__(self, root, client):
        self.client = client
        self.root = root 
        self.root.title("Photo Storage Application")
        self.current_album = None
        self.current_page = 0
        self.page_size = 10

        # Configure root window
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Define colors and fonts
        self.colors = {
            "primary": "#4a90e2",
            "secondary": "#f5f5f5",
            "accent": "#50c878",
            "text": "#333333",
            "error": "#e74c3c",
            "success": "#2ecc71"
        }
        self.fonts = {
            "title": ("Helvetica", 16, "bold"),
            "header": ("Helvetica", 12, "bold"),
            "body": ("Helvetica", 10),
            "button": ("Helvetica", 10, "bold")
        }

        # Create main frames
        self.login_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.main_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.create_album_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.upload_photo_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.view_album_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.delete_album_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.edit_privileges_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)
        self.delete_images_frame = tk.Frame(self.root, bg=self.colors["secondary"], padx=20, pady=20)

        self.create_login_frame()
        self.create_main_frame()
        self.create_create_album_frame()
        self.create_upload_photo_frame()
        self.create_view_album_frame()
        self.create_delete_album_frame()
        self.create_edit_privileges_frame()
        self.create_delete_images_frame()

        self.login_frame.pack(expand=True, fill="both")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_styled_button(self, parent, text, command, bg_color=None):
        if bg_color is None:
            bg_color = self.colors["primary"]
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg="white",
            font=self.fonts["button"],
            padx=10,
            pady=5,
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )

    def create_styled_label(self, parent, text, font_type="body"):
        return tk.Label(
            parent,
            text=text,
            font=self.fonts[font_type],
            bg=self.colors["secondary"],
            fg=self.colors["text"]
        )

    def create_styled_entry(self, parent):
        return tk.Entry(
            parent,
            font=self.fonts["body"],
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#cccccc",
            highlightcolor=self.colors["primary"]
        )

    def create_login_frame(self):
        # Title
        title_label = self.create_styled_label(self.login_frame, "Photo Storage App", "title")
        title_label.pack(pady=20)

        # Login form container
        form_frame = tk.Frame(self.login_frame, bg=self.colors["secondary"])
        form_frame.pack(pady=20)

        # Username
        username_label = self.create_styled_label(form_frame, "Username")
        username_label.pack(pady=5)
        self.username_entry = self.create_styled_entry(form_frame)
        self.username_entry.pack(pady=5, ipadx=5, ipady=5)

        # Password
        password_label = self.create_styled_label(form_frame, "Password")
        password_label.pack(pady=5)
        self.password_entry = self.create_styled_entry(form_frame)
        self.password_entry.configure(show="*")
        self.password_entry.pack(pady=5, ipadx=5, ipady=5)

        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.colors["secondary"])
        button_frame.pack(pady=20)

        self.login_button = self.create_styled_button(button_frame, "Login", self.login)
        self.login_button.pack(side="left", padx=10)

        self.signup_button = self.create_styled_button(button_frame, "Signup", self.signup, self.colors["accent"])
        self.signup_button.pack(side="left", padx=10)

    def create_main_frame(self):
        # Title
        title_label = self.create_styled_label(self.main_frame, "Welcome to Photo Storage", "title")
        title_label.pack(pady=20)

        # Menu container
        menu_frame = tk.Frame(self.main_frame, bg=self.colors["secondary"])
        menu_frame.pack(pady=20)

        # Photo function buttons (in a grid, removed List Existing Users)
        photo_buttons = [
            ("Create Album", self.show_create_album_frame),
            ("Upload Photos", self.show_upload_photo_frame),
            ("View Album", self.show_view_album_frame),
            ("Delete Album", self.show_delete_album_frame),
            ("Edit Album Privileges", self.show_edit_privileges_frame),
            ("Delete Images", self.show_delete_images_frame),
        ]
        for i, (text, command) in enumerate(photo_buttons):
            btn = self.create_styled_button(menu_frame, text, command)
            btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
        for i in range(3):
            menu_frame.grid_columnconfigure(i, weight=1)

        # Separator
        separator = tk.Frame(self.main_frame, height=2, bd=0, relief="ridge", bg="#cccccc")
        separator.pack(fill="x", padx=30, pady=(10, 0))

        # Logout and Delete Account buttons (separated)
        account_frame = tk.Frame(self.main_frame, bg=self.colors["secondary"])
        account_frame.pack(pady=15)
        self.logout_button = self.create_styled_button(account_frame, "Logout", self.logout, bg_color=self.colors["primary"])
        self.logout_button.pack(side="left", padx=10)
        self.delete_account_button = self.create_styled_button(account_frame, "Delete Account", self.delete_account, bg_color=self.colors["error"])
        self.delete_account_button.pack(side="left", padx=10)

    def create_create_album_frame(self):
        # Title
        title_label = self.create_styled_label(self.create_album_frame, "Create Album", "title")
        title_label.pack(pady=20)

        # Form container
        form_frame = tk.Frame(self.create_album_frame, bg=self.colors["secondary"])
        form_frame.pack(pady=10)

        # Album name
        album_label = self.create_styled_label(form_frame, "Album Name:")
        album_label.pack(pady=5)
        self.new_album_entry = self.create_styled_entry(form_frame)
        self.new_album_entry.pack(pady=5, ipadx=5, ipady=5)

        # Editors
        editors_label = self.create_styled_label(form_frame, "Editors (comma-separated usernames):")
        editors_label.pack(pady=5)
        self.editors_entry = self.create_styled_entry(form_frame)
        self.editors_entry.pack(pady=5, ipadx=5, ipady=5)

        # User list label
        userlist_label = self.create_styled_label(form_frame, "All Users:")
        userlist_label.pack(pady=(15, 5))
        userlist_frame = tk.Frame(form_frame, bg=self.colors["secondary"])
        userlist_frame.pack(pady=5, fill="x")
        self.all_users_listbox = tk.Listbox(
            userlist_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=6,
            width=30
        )
        self.all_users_listbox.pack(side="left", fill="both", expand=True)
        userlist_scrollbar = tk.Scrollbar(userlist_frame, orient="vertical", command=self.all_users_listbox.yview)
        userlist_scrollbar.pack(side="right", fill="y")
        self.all_users_listbox.config(yscrollcommand=userlist_scrollbar.set)

        # Create button
        self.create_button = self.create_styled_button(form_frame, "Create Album", self.create_album)
        self.create_button.pack(pady=20)

        # Back button
        self.back_button = self.create_styled_button(self.create_album_frame, "Back", self.show_main_frame)
        self.back_button.pack(pady=10)

    def create_upload_photo_frame(self):
        # Title
        title_label = self.create_styled_label(self.upload_photo_frame, "Upload Photo", "title")
        title_label.pack(pady=20)

        # Album selection
        album_frame = tk.Frame(self.upload_photo_frame, bg=self.colors["secondary"])
        album_frame.pack(pady=10)

        album_label = self.create_styled_label(album_frame, "Select Album:")
        album_label.pack(pady=5)

        album_list_frame = tk.Frame(album_frame, bg=self.colors["secondary"])
        album_list_frame.pack(pady=5, fill="x")
        self.upload_album_list = tk.Listbox(
            album_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=10
        )
        self.upload_album_list.pack(side="left", fill="x", expand=True)
        upload_album_scrollbar = tk.Scrollbar(album_list_frame, orient="vertical", command=self.upload_album_list.yview)
        upload_album_scrollbar.pack(side="right", fill="y")
        self.upload_album_list.config(yscrollcommand=upload_album_scrollbar.set)
        self.upload_album_list.bind('<<ListboxSelect>>', self.on_upload_album_select)

        # Upload button
        self.upload_photo_button = self.create_styled_button(album_frame, "Upload Photo", self.upload_photo)
        self.upload_photo_button.pack(pady=10)
        self.upload_photo_button.config(state="disabled")

        # Back button
        self.back_button = self.create_styled_button(self.upload_photo_frame, "Back", self.show_main_frame)
        self.back_button.pack(pady=10)

    def create_view_album_frame(self):
        # Title
        title_label = self.create_styled_label(self.view_album_frame, "View Album", "title")
        title_label.pack(pady=10)

        # Main container
        main_container = tk.Frame(self.view_album_frame, bg=self.colors["secondary"])
        main_container.pack(fill="both", expand=True)

        # Left panel (album list)
        left_panel = tk.Frame(main_container, bg=self.colors["secondary"])
        left_panel.pack(side="left", fill="y", padx=10)

        album_label = self.create_styled_label(left_panel, "Select Album:")
        album_label.pack(pady=5)

        view_album_list_frame = tk.Frame(left_panel, bg=self.colors["secondary"])
        view_album_list_frame.pack(pady=5, fill="y", expand=True)
        self.view_album_list = tk.Listbox(
            view_album_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            width=30,
            height=12  # Reduced height
        )
        self.view_album_list.pack(side="left", fill="y", expand=True)
        view_album_scrollbar = tk.Scrollbar(view_album_list_frame, orient="vertical", command=self.view_album_list.yview)
        view_album_scrollbar.pack(side="right", fill="y")
        self.view_album_list.config(yscrollcommand=view_album_scrollbar.set)
        self.view_album_list.bind('<<ListboxSelect>>', self.on_view_album_select)

        # Back button in left panel
        self.back_button = self.create_styled_button(left_panel, "Back", self.show_main_frame)
        self.back_button.pack(pady=10)

        # Right panel (photo display)
        right_panel = tk.Frame(main_container, bg=self.colors["secondary"])
        right_panel.pack(side="right", fill="both", expand=True, padx=10)

        # Photo canvas
        self.photo_canvas = tk.Canvas(
            right_panel,
            bg="white",
            width=400,
            height=300,  # Restored to original height
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.photo_canvas.pack(pady=5)  # Reduced padding

        # Photo list with scrollbar
        photo_list_frame = tk.Frame(right_panel, bg=self.colors["secondary"])
        photo_list_frame.pack(pady=5, fill="x")
        self.photo_list = tk.Listbox(
            photo_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=9
        )
        self.photo_list.pack(side="left", fill="x", expand=True)
        photo_list_scrollbar = tk.Scrollbar(photo_list_frame, orient="vertical", command=self.photo_list.yview)
        photo_list_scrollbar.pack(side="right", fill="y")
        self.photo_list.config(yscrollcommand=photo_list_scrollbar.set)
        self.photo_list.bind('<<ListboxSelect>>', self.on_photo_select)

        # Navigation buttons
        nav_frame = tk.Frame(right_panel, bg=self.colors["secondary"])
        nav_frame.pack(pady=5)

        self.prev_button = self.create_styled_button(nav_frame, "Previous", self.prev_photo_page)
        self.prev_button.pack(side="left", padx=5)
        self.prev_button.config(state="disabled")

        self.next_button = self.create_styled_button(nav_frame, "Next", self.next_photo_page)
        self.next_button.pack(side="left", padx=5)
        self.next_button.config(state="disabled")

    def create_delete_album_frame(self):
        # Title
        title_label = self.create_styled_label(self.delete_album_frame, "Delete Album", "title")
        title_label.pack(pady=20)

        # Album selection
        album_frame = tk.Frame(self.delete_album_frame, bg=self.colors["secondary"])
        album_frame.pack(pady=10)

        album_label = self.create_styled_label(album_frame, "Select Album to Delete:")
        album_label.pack(pady=5)

        delete_album_list_frame = tk.Frame(album_frame, bg=self.colors["secondary"])
        delete_album_list_frame.pack(pady=5, fill="x")
        self.delete_album_list = tk.Listbox(
            delete_album_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=10
        )
        self.delete_album_list.pack(side="left", fill="x", expand=True)
        delete_album_scrollbar = tk.Scrollbar(delete_album_list_frame, orient="vertical", command=self.delete_album_list.yview)
        delete_album_scrollbar.pack(side="right", fill="y")
        self.delete_album_list.config(yscrollcommand=delete_album_scrollbar.set)
        self.delete_album_list.bind('<<ListboxSelect>>', self.on_delete_album_select)

        # Delete button
        self.delete_button = self.create_styled_button(album_frame, "Delete", self.delete_album, self.colors["error"])
        self.delete_button.pack(pady=10)
        self.delete_button.config(state="disabled")

        # Back button
        self.back_button = self.create_styled_button(self.delete_album_frame, "Back", self.show_main_frame)
        self.back_button.pack(pady=10)

    def create_edit_privileges_frame(self):
        # Title
        title_label = self.create_styled_label(self.edit_privileges_frame, "Edit Album Privileges", "title")
        title_label.pack(pady=20)

        # Main container
        main_container = tk.Frame(self.edit_privileges_frame, bg=self.colors["secondary"])
        main_container.pack(fill="both", expand=True)

        # Left panel (album list + back button)
        left_panel = tk.Frame(main_container, bg=self.colors["secondary"])
        left_panel.pack(side="left", fill="y", padx=10)

        album_label = self.create_styled_label(left_panel, "Select Album:")
        album_label.pack(pady=5)

        album_list_frame = tk.Frame(left_panel, bg=self.colors["secondary"])
        album_list_frame.pack(pady=5, fill="y", expand=True)
        self.priv_album_list = tk.Listbox(
            album_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            width=30,
            height=12
        )
        self.priv_album_list.pack(side="left", fill="y", expand=True)
        album_scrollbar = tk.Scrollbar(album_list_frame, orient="vertical", command=self.priv_album_list.yview)
        album_scrollbar.pack(side="right", fill="y")
        self.priv_album_list.config(yscrollcommand=album_scrollbar.set)
        self.priv_album_list.bind('<<ListboxSelect>>', self.on_priv_album_select)

        # Back button under album list
        self.back_button = self.create_styled_button(left_panel, "Back", self.show_main_frame)
        self.back_button.pack(pady=10)

        # Right panel (editors and non-editors)
        right_panel = tk.Frame(main_container, bg=self.colors["secondary"])
        right_panel.pack(side="right", fill="both", expand=True, padx=10)

        # Current editors
        editors_label = self.create_styled_label(right_panel, "Current Editors:")
        editors_label.pack(pady=5)
        editors_frame = tk.Frame(right_panel, bg=self.colors["secondary"])
        editors_frame.pack(pady=5, fill="x")
        self.editors_list = tk.Listbox(
            editors_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=6,
            width=30
        )
        self.editors_list.pack(side="left", fill="both", expand=True)
        editors_scrollbar = tk.Scrollbar(editors_frame, orient="vertical", command=self.editors_list.yview)
        editors_scrollbar.pack(side="right", fill="y")
        self.editors_list.config(yscrollcommand=editors_scrollbar.set)

        # Non-editors label and listbox with scrollbar
        noneditors_label = self.create_styled_label(right_panel, "Non-Editors:")
        noneditors_label.pack(pady=(10, 5))
        noneditors_frame = tk.Frame(right_panel, bg=self.colors["secondary"])
        noneditors_frame.pack(pady=5, fill="x")
        self.noneditors_listbox = tk.Listbox(
            noneditors_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=6,
            width=30
        )
        self.noneditors_listbox.pack(side="left", fill="both", expand=True)
        noneditors_scrollbar = tk.Scrollbar(noneditors_frame, orient="vertical", command=self.noneditors_listbox.yview)
        noneditors_scrollbar.pack(side="right", fill="y")
        self.noneditors_listbox.config(yscrollcommand=noneditors_scrollbar.set)
        self.noneditors_listbox.bind('<<ListboxSelect>>', self.on_noneditor_select)

        # Add/Remove editor controls side by side
        controls_frame = tk.Frame(right_panel, bg=self.colors["secondary"])
        controls_frame.pack(pady=10)
        add_label = self.create_styled_label(controls_frame, "Add Editor (username):")
        add_label.grid(row=0, column=0, columnspan=2, pady=5)
        self.add_editor_entry = self.create_styled_entry(controls_frame)
        self.add_editor_entry.grid(row=1, column=0, columnspan=2, padx=5, ipadx=5, ipady=5, sticky="ew")
        self.add_editor_button = self.create_styled_button(controls_frame, "Add Editor", self.add_editor)
        self.add_editor_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.remove_editor_button = self.create_styled_button(controls_frame, "Remove Selected Editor", self.remove_editor, self.colors["error"])
        self.remove_editor_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)

    def create_delete_images_frame(self):
        # Title
        title_label = self.create_styled_label(self.delete_images_frame, "Delete Images", "title")
        title_label.pack(pady=20)

        # Main container
        main_container = tk.Frame(self.delete_images_frame, bg=self.colors["secondary"])
        main_container.pack(fill="both", expand=True)

        # Left panel (album list)
        left_panel = tk.Frame(main_container, bg=self.colors["secondary"])
        left_panel.pack(side="left", fill="y", padx=10)

        album_label = self.create_styled_label(left_panel, "Select Album:")
        album_label.pack(pady=5)

        delete_img_album_list_frame = tk.Frame(left_panel, bg=self.colors["secondary"])
        delete_img_album_list_frame.pack(pady=5, fill="y", expand=True)
        self.delete_img_album_list = tk.Listbox(
            delete_img_album_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            width=30,
            height=15
        )
        self.delete_img_album_list.pack(side="left", fill="y", expand=True)
        delete_img_album_scrollbar = tk.Scrollbar(delete_img_album_list_frame, orient="vertical", command=self.delete_img_album_list.yview)
        delete_img_album_scrollbar.pack(side="right", fill="y")
        self.delete_img_album_list.config(yscrollcommand=delete_img_album_scrollbar.set)
        self.delete_img_album_list.bind('<<ListboxSelect>>', self.on_delete_img_album_select)

        # Right panel (image list)
        right_panel = tk.Frame(main_container, bg=self.colors["secondary"])
        right_panel.pack(side="right", fill="both", expand=True, padx=10)

        image_label = self.create_styled_label(right_panel, "Your Images in Album:")
        image_label.pack(pady=5)

        delete_img_list_frame = tk.Frame(right_panel, bg=self.colors["secondary"])
        delete_img_list_frame.pack(pady=5, fill="both", expand=True)
        self.delete_img_list = tk.Listbox(
            delete_img_list_frame,
            font=self.fonts["body"],
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            height=15
        )
        self.delete_img_list.pack(side="left", fill="both", expand=True)
        delete_img_list_scrollbar = tk.Scrollbar(delete_img_list_frame, orient="vertical", command=self.delete_img_list.yview)
        delete_img_list_scrollbar.pack(side="right", fill="y")
        self.delete_img_list.config(yscrollcommand=delete_img_list_scrollbar.set)
        self.delete_img_list.bind('<<ListboxSelect>>', self.on_delete_img_select)

        # Delete button
        self.delete_img_button = self.create_styled_button(right_panel, "Delete Selected Image", self.delete_selected_image, self.colors["error"])
        self.delete_img_button.pack(pady=10)
        self.delete_img_button.config(state="disabled")

        # Back button
        self.back_button = self.create_styled_button(self.delete_images_frame, "Back", self.show_main_frame)
        self.back_button.pack(pady=10)

    def show_create_album_frame(self):
        self.main_frame.pack_forget()
        self.create_album_frame.pack()
        self.new_album_entry.delete(0, tk.END)
        self.editors_entry.delete(0, tk.END)
        self.refresh_all_users_list()

    def show_upload_photo_frame(self):
        self.main_frame.pack_forget()
        self.upload_photo_frame.pack()
        self.refresh_upload_albums()

    def show_view_album_frame(self):
        self.main_frame.pack_forget()
        self.view_album_frame.pack()
        # Clear photo canvas and photo list, reset pagination
        self.photo_canvas.delete("all")
        self.photo_list.delete(0, tk.END)
        self.current_album = None
        self.current_page = 0
        self.prev_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.refresh_view_albums()

    def show_delete_album_frame(self):
        self.main_frame.pack_forget()
        self.delete_album_frame.pack()
        self.refresh_delete_albums()

    def show_edit_privileges_frame(self):
        self.main_frame.pack_forget()
        self.edit_privileges_frame.pack()
        self.priv_album_list.selection_clear(0, tk.END)
        self.editors_list.delete(0, tk.END)
        self.noneditors_listbox.delete(0, tk.END)
        self.add_editor_entry.delete(0, tk.END)
        self.refresh_priv_album_list()

    def show_delete_images_frame(self):
        self.main_frame.pack_forget()
        self.delete_images_frame.pack()
        self.refresh_delete_img_album_list()
        self.delete_img_list.delete(0, tk.END)
        self.delete_img_button.config(state="disabled")

    def show_main_frame(self):
        # Close the photo popup if it exists
        if hasattr(self, '_photo_popup') and self._photo_popup is not None:
            try:
                self._photo_popup.destroy()
            except Exception:
                pass
            self._photo_popup = None
        self.create_album_frame.pack_forget()
        self.upload_photo_frame.pack_forget()
        self.view_album_frame.pack_forget()
        self.delete_album_frame.pack_forget()
        self.edit_privileges_frame.pack_forget()
        self.delete_images_frame.pack_forget()
        self.main_frame.pack()

    def refresh_upload_albums(self):
        self.upload_album_list.delete(0, tk.END)
        success, albums = self.client.fetch_albums()
        if success:
            for album in albums:
                self.upload_album_list.insert(tk.END, album)
        else:
            messagebox.showerror("Error", "Failed to fetch albums")

    def refresh_view_albums(self):
        self.view_album_list.delete(0, tk.END)
        success, albums = self.client.fetch_albums()
        if success:
            for album in albums:
                self.view_album_list.insert(tk.END, album)
        else:
            messagebox.showerror("Error", "Failed to fetch albums")

    def refresh_delete_albums(self):
        self.delete_album_list.delete(0, tk.END)
        success, albums = self.client.fetch_albums()
        if success:
            for album in albums:
                self.delete_album_list.insert(tk.END, album)
        else:
            messagebox.showerror("Error", "Failed to fetch albums")

    def refresh_priv_album_list(self):
        self.priv_album_list.delete(0, tk.END)
        success, albums = self.client.fetch_albums()
        if success:
            for album in albums:
                self.priv_album_list.insert(tk.END, album)
        else:
            messagebox.showerror("Error", "Failed to fetch albums")

    def on_upload_album_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_album = event.widget.get(selection[0])
            self.upload_photo_button.config(state="normal")

    def on_view_album_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_album = event.widget.get(selection[0])
            # Clear the photo canvas when switching albums
            self.photo_canvas.delete("all")
            self.refresh_photos()
            self.prev_button.config(state="normal")
            self.next_button.config(state="normal")

    def on_delete_album_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_album = event.widget.get(selection[0])
            self.delete_button.config(state="normal")

    def on_photo_select(self, event):
        selection = event.widget.curselection()
        if selection:
            photo_name = event.widget.get(selection[0])
            success, photos = self.client.fetch_photos(self.current_album, self.current_page, self.page_size)
            if success:
                for photo in photos:
                    if photo["metadata"]["image_name"] == photo_name:
                        self.display_photo(photo["data"], photo["metadata"]["image_name"])
                        break

    def display_photo(self, image_data, image_name):
        # Display the photo as a thumbnail on the canvas
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image)
            self.photo_canvas.delete("all")
            self.photo_canvas.create_image(0, 0, anchor="nw", image=photo)
            self.photo_canvas.image = photo
            # Store the full image data and name for enlargement
            self._last_full_image_data = image_data
            self._last_full_image_name = image_name
            # Bind click event to canvas for enlargement
            self.photo_canvas.bind("<Button-1>", self._on_canvas_click_enlarge)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display photo: {str(e)}")

    def _on_canvas_click_enlarge(self, event):
        if hasattr(self, '_last_full_image_data') and hasattr(self, '_last_full_image_name'):
            self.show_enlarged_photo(self._last_full_image_data, self._last_full_image_name)

    def show_enlarged_photo(self, image_data, image_name):
        # Create a new popup window and track it
        popup = tk.Toplevel(self.root)
        self._photo_popup = popup
        popup.title(f"Viewing: {image_name}")
        popup.geometry("1000x800")
        popup.configure(bg="#f0f0f0")
        try:
            image = Image.open(io.BytesIO(image_data))
            max_width, max_height = 1000, 800
            image.thumbnail((max_width, max_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            canvas = tk.Canvas(popup, width=max_width, height=max_height, bg="white", highlightthickness=0)
            canvas.pack(expand=True)
            x = (max_width - image.width) // 2
            y = (max_height - image.height) // 2
            canvas.create_image(x, y, anchor="nw", image=photo)
            canvas.image = photo  # Keep reference
        except Exception as e:
            tk.Label(popup, text=f"Failed to display photo: {str(e)}", fg="red", bg="#f0f0f0").pack(pady=20)

    def prev_photo_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_photos()

    def next_photo_page(self):
        self.current_page += 1
        self.refresh_photos()

    def refresh_photos(self):
        if not self.current_album:
            return

        self.photo_list.delete(0, tk.END)
        success, photos = self.client.fetch_photos(self.current_album, self.current_page, self.page_size)
        if success:
            # Update button states based on pagination
            self.prev_button.config(state="normal" if self.current_page > 0 else "disabled")
            
            # If we got fewer photos than page size, we're on the last page
            has_next_page = len(photos) == self.page_size
            self.next_button.config(state="normal" if has_next_page else "disabled")
            
            # Display photos
            for photo in photos:
                self.photo_list.insert(tk.END, photo["metadata"]["image_name"])
        else:
            # If fetch failed, disable both buttons
            self.prev_button.config(state="disabled")
            self.next_button.config(state="disabled")
            messagebox.showerror("Error", "Failed to fetch photos")

    def upload_photo(self):
        if not self.current_album:
            messagebox.showerror("Error", "Please select an album first")
            return

        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("JPEG files", "*.jpg *.jpeg"), ("PNG files", "*.png")]
        )
        if file_path:
            success, message = self.client.upload_image(file_path, self.current_album)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def create_album(self):
        album_name = self.new_album_entry.get()
        editors_raw = self.editors_entry.get()
        editors = [e.strip() for e in editors_raw.split(',') if e.strip()]
        if not album_name:
            messagebox.showerror("Error", "Please enter an album name")
            return

        success, message = self.client.create_album(album_name)
        if success:
            # Add editors if any
            for editor in editors:
                if editor != self.client.username:
                    self.client.add_album_editor(album_name, editor)
            messagebox.showinfo("Success", message)
            self.show_main_frame()
        else:
            messagebox.showerror("Error", message)

    def delete_album(self):
        if not self.current_album:
            messagebox.showerror("Error", "Please select an album first")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete album '{self.current_album}'?"):
            success, message = self.client.delete_album(self.current_album)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_delete_albums()
                self.delete_button.config(state="disabled")
            else:
                messagebox.showerror("Error", message)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message, _ = self.client.login(username, password)
        if success:
            messagebox.showinfo("Login Successful", message)  
            self.login_frame.pack_forget()
            self.main_frame.pack()
        else: 
            messagebox.showerror("Login Failed", message)

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.client.signup(username, password)
        if success:
            messagebox.showinfo("Signup Successful", message)
            self.login_frame.pack_forget()
            self.main_frame.pack()
        else: 
            messagebox.showerror("Signup Failed", message)

    def logout(self):
        success, message = self.client.logout()
        if success:
            messagebox.showinfo("Logout Successful", message)
            self.main_frame.pack_forget()
            self.login_frame.pack()
        else: 
            messagebox.showerror("Logout Failed", message)

    def delete_account(self):
        if not self.client.username:
            return False, "You are not logged in! Delete account unsuccessful"
        success, response = self.client.delete_account()
        if success:
            messagebox.showinfo("Delete Account Successful", response)
            self.root.destroy()
        else:
            messagebox.showerror("Delete Account Failed", response)

    def on_priv_album_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.selected_priv_album = event.widget.get(selection[0])
            self.refresh_editors_list()
            self.refresh_noneditors_list()

    def refresh_editors_list(self):
        self.editors_list.delete(0, tk.END)
        # Fetch editors from album metadata (server-side)
        editors = self.client.get_album_editors(self.selected_priv_album)
        for editor in editors:
            self.editors_list.insert(tk.END, editor)

    def add_editor(self):
        username = self.add_editor_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username to add as editor.")
            return
        success, message = self.client.add_album_editor(self.selected_priv_album, username)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_editors_list()
            self.refresh_noneditors_list()
        else:
            messagebox.showerror("Error", message)

    def remove_editor(self):
        selection = self.editors_list.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an editor to remove.")
            return
        username = self.editors_list.get(selection[0])
        success, message = self.client.remove_album_editor(self.selected_priv_album, username)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_editors_list()
            self.refresh_noneditors_list()
        else:
            messagebox.showerror("Error", message)

    def on_closing(self):
        if self.client.username: 
            self.client.logout()
        self.root.destroy()

    def refresh_delete_img_album_list(self):
        self.delete_img_album_list.delete(0, tk.END)
        success, albums = self.client.fetch_albums()
        if success:
            for album in albums:
                self.delete_img_album_list.insert(tk.END, album)
        else:
            messagebox.showerror("Error", "Failed to fetch albums")

    def on_delete_img_album_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.selected_delete_img_album = event.widget.get(selection[0])
            self.refresh_delete_img_list()

    def refresh_delete_img_list(self):
        self.delete_img_list.delete(0, tk.END)
        # Fetch all images in the album, filter by current user
        success, photos = self.client.fetch_photos(self.selected_delete_img_album, 0, 1000)  # get all
        if success:
            for photo in photos:
                if photo["metadata"]["username"] == self.client.username:
                    self.delete_img_list.insert(tk.END, photo["metadata"]["image_name"])
        else:
            messagebox.showerror("Error", "Failed to fetch images")

    def on_delete_img_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.selected_delete_img = event.widget.get(selection[0])
            self.delete_img_button.config(state="normal")
        else:
            self.selected_delete_img = None
            self.delete_img_button.config(state="disabled")

    def delete_selected_image(self):
        if not hasattr(self, 'selected_delete_img_album') or not hasattr(self, 'selected_delete_img'):
            messagebox.showerror("Error", "Please select an album and an image to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete image '{self.selected_delete_img}'?"):
            success, message = self.client.delete_image(self.selected_delete_img_album, self.selected_delete_img)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_delete_img_list()
                self.delete_img_button.config(state="disabled")
            else:
                messagebox.showerror("Error", message)

    def refresh_all_users_list(self):
        # Fetch all users and display in the listbox
        self.all_users_listbox.delete(0, tk.END)
        success, users = self.client.list("")  # Empty pattern = all users
        if success:
            for user in users:
                self.all_users_listbox.insert(tk.END, user)
        else:
            self.all_users_listbox.insert(tk.END, "Failed to fetch users")

    def refresh_noneditors_list(self):
        # Fetch all users and subtract current editors
        self.noneditors_listbox.delete(0, tk.END)
        success, all_users = self.client.list("")
        if not success:
            self.noneditors_listbox.insert(tk.END, "Failed to fetch users")
            return
        editors = self.client.get_album_editors(self.selected_priv_album)
        non_editors = [u for u in all_users if u not in editors]
        for user in non_editors:
            self.noneditors_listbox.insert(tk.END, user)

    def on_noneditor_select(self, event):
        selection = event.widget.curselection()
        if selection:
            username = event.widget.get(selection[0])
            self.add_editor_entry.delete(0, tk.END)
            self.add_editor_entry.insert(0, username)

if __name__ == "__main__":
    try:
        print("CLIENT HOST:", CLIENT_HOST)
        client = Client(SERVER_HOST, SERVER_PORT, CLIENT_HOST)
        root = tk.Tk()
        app = PhotoApp(root, client)
        root.mainloop()
    except KeyboardInterrupt:
        print("Client interrupted by user, exiting...")
    finally:
        if client.username:
            client.logout()
