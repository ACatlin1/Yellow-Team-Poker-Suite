"""
**************************************************************************

lobby.py is for:

the initial screen to
enter a username
pick single or multiplayer
and pick game rules

**************************************************************************
"""

import tkinter as tk
from ui.widgets import StyledButton, StyledEntry, StyledLabel


class LobbyScreen(tk.Frame):
    def __init__(self, master, start_callback):
        # Main lobby screen where player enters username and chooses mode
        super().__init__(master)

        # Callback function triggered when starting a game
        self.start_callback = start_callback

        # Fill entire window
        self.pack(fill="both", expand=True)

        # Background matches poker table theme
        self.configure(bg="#0b3d0b")

        # Stores username input (reactive Tkinter variable)
        self.username_value = tk.StringVar()

        self.build()

    def build(self):
        # ---------- TOP BAR ----------
        top = tk.Frame(self, bg="#0b3d0b")
        top.pack(fill="x", pady=10)

        # Title centered at top
        title = StyledLabel(top, "Poker Suite", size=22, bold=True)
        title.pack()

        # Username input area aligned to the right
        user_frame = tk.Frame(top, bg="#0b3d0b")
        user_frame.pack(side="right", padx=20)

        self.username_entry = StyledEntry(user_frame)
        self.username_entry.pack(side="left", padx=5)

        confirm_btn = StyledButton(user_frame, "OK", self.confirm_username, width=5)
        confirm_btn.pack(side="left")

        # ---------- RIGHT SIDE MENU ----------
        right_menu = tk.Frame(self, bg="#0b3d0b")
        right_menu.pack(side="right", padx=80, pady=150)

        # Game options
        StyledButton(right_menu, "Singleplayer Table", self.singleplayer).pack(pady=5)
        StyledButton(right_menu, "Multiplayer Table", self.multiplayer).pack(pady=5)
        StyledButton(right_menu, "View Stats", self.view_stats).pack(pady=5)
        StyledButton(right_menu, "Exit", self.exit_app).pack(pady=5)

    def confirm_username(self):
        # Save username from input field into StringVar
        self.username_value.set(self.username_entry.get())
        print(f"Username set to: {self.username_value.get()}")

    def singleplayer(self):
        # Start game using entered username (fallback to "Player")
        name = self.username_value.get() or "Player"
        self.start_callback(name)

    def multiplayer(self):
        # Placeholder for future multiplayer logic
        print("Multiplayer selected")

    def view_stats(self):
        # Placeholder for stats screen
        print("View stats")

    def exit_app(self):
        # Closes the application
        self.master.quit()
