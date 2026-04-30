"""
**************************************************************************

lobby.py is for:

the initial screen to
enter a username   -- moved to Auth
pick single or multiplayer
pick game rules
pick the number of bots to play against (local)

**************************************************************************
"""

import tkinter as tk
from ui.widgets import StyledButton, StyledEntry, StyledLabel


class LobbyScreen(tk.Frame):

    def __init__(self, master, db, username, start_callback):
        # Main lobby screen where player enters username and chooses mode
        super().__init__(master)
        self.master = master
        self.db = db
        self.username = username
        self.start_callback = start_callback

        # Configuration
        self.configure(bg="#0b3d0b")

        self.variant_var = tk.StringVar(value="Texas Hold'em") 
        self.bot_var = tk.IntVar(value=1)

        self.build()


    def build(self):
        # ---------- TOP BAR ----------
        top = tk.Frame(self, bg="#0b3d0b")
        top.pack(fill="x", pady=10)

        # Title centered at top
        title = StyledLabel(top, "Poker Suite", size=22, bold=True)
        title.pack()

        """ Replaced this with auth screen
        # Username input area aligned to the right
        user_frame = tk.Frame(top, bg="#0b3d0b")
        user_frame.pack(side="right", padx=20)

        self.username_entry = StyledEntry(user_frame)
        self.username_entry.pack(side="left", padx=5)

        confirm_btn = StyledButton(user_frame, "OK", self.confirm_username, width=5)
        confirm_btn.pack(side="left")"""

        # ---------- RIGHT SIDE MENU ----------
        right_menu = tk.Frame(self, bg="#0b3d0b")
        right_menu.pack(side="right", padx=80, pady=150)

        # Game options
        StyledButton(right_menu, "Singleplayer Table", self.singleplayer).pack(pady=5)
        StyledButton(right_menu, "Multiplayer Table", self.multiplayer).pack(pady=5)
        StyledButton(right_menu, "View Stats", self.view_stats).pack(pady=5)
        StyledButton(right_menu, "Exit", self.exit_app).pack(pady=5)

        if self.db.has_saved_game(self.username):
            resume_btn = tk.Button(
                self, 
                text="Resume Saved Game", 
                command=lambda: self.start_callback(None, None, load_saved=True),
                bg="#f39c12", # A different color to distinguish it
                fg="white"
            )
            resume_btn.pack(pady=10)

        # ---------- GAME SETTINGS ----------
        settings_frame = tk.Frame(self, bg="#0b3d0b")
        settings_frame.pack(pady=20)

        # Variant Selection
        StyledLabel(settings_frame, "Game Variant:", size=12).grid(row=0, column=0, padx=10)
        variant_menu = tk.OptionMenu(self, self.variant_var, "Texas Hold'em", "5-Card Draw", "7-Card Stud")
        variant_menu.config(bg="#2e7d32", fg="white", font=("Arial", 10, "bold"), width=15)
        variant_menu.grid(row=0, column=1, padx=10, in_=settings_frame)

        # Bot Count Selection
        StyledLabel(settings_frame, "Bots:", size=12).grid(row=1, column=0, padx=10, pady=10)
        self.bot_count_spin = tk.Spinbox(settings_frame, from_=1, to=5, width=5, font=("Arial", 12))
        self.bot_count_spin.grid(row=1, column=1, padx=10)


    """ No longer needed with the authorization screen
    def confirm_username(self):
        # Save username from input field into StringVar
        self.self.username.set(self.username_entry.get())
        print(f"Username set to: {self.self.username.get()}")"""


    def singleplayer(self):
        variant = self.variant_var.get()
        bot_count = int(self.bot_count_spin.get())
        self.start_callback(variant, bot_count, is_multiplayer=False)


    def multiplayer(self):
        variant = self.variant_var.get()
        self.start_callback(variant, bot_count=0, is_multiplayer=True)


    def view_stats(self):
        self.master.show_stats()


    def exit_app(self):
        # Closes the application
        self.master.quit()
