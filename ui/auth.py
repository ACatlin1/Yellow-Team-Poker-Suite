"""
**************************************************************************

auth.py is for:

A new authentication screen

**************************************************************************
"""

import tkinter as tk
from ui.widgets import StyledButton, StyledEntry, StyledLabel

class AuthScreen(tk.Frame):
    def __init__(self, master, login_callback, register_callback, guest_callback):
        super().__init__(master)
        self.login_callback = login_callback
        self.register_callback = register_callback
        self.guest_callback = guest_callback

        self.pack(fill="both", expand=True)
        self.configure(bg="#0b3d0b")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.build()

    def build(self):
        # Center Frame
        center = tk.Frame(self, bg="#0b3d0b")
        center.place(relx=0.5, rely=0.5, anchor="center")

        StyledLabel(center, "Welcome to Poker Suite", size=24, bold=True).pack(pady=20)

        # Inputs
        StyledLabel(center, "Username:", size=12).pack()
        user_entry = tk.Entry(center, textvariable=self.username_var, font=("Arial", 14))
        user_entry.pack(pady=5, ipady=5)

        StyledLabel(center, "Password:", size=12).pack()
        pwd_entry = tk.Entry(center, textvariable=self.password_var, show="*", font=("Arial", 14))
        pwd_entry.pack(pady=5, ipady=5)

        # Status Label (for error messages)
        self.status_label = tk.Label(center, text="", bg="#0b3d0b", fg="red", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(center, bg="#0b3d0b")
        btn_frame.pack(pady=15)

        StyledButton(btn_frame, "Login", self.login).grid(row=0, column=0, padx=5)
        StyledButton(btn_frame, "Register", self.register).grid(row=0, column=1, padx=5)
        
        StyledButton(center, "Play Offline (Guest)", self.guest).pack(pady=10)

    def login(self):
        self.login_callback(self.username_var.get(), self.password_var.get(), self.status_label)

    def register(self):
        self.register_callback(self.username_var.get(), self.password_var.get(), self.status_label)

    def guest(self):
        self.guest_callback()