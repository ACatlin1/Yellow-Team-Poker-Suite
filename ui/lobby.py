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

        # ---------- GAME SETTINGS ----------
        settings_frame = tk.Frame(self, bg="#0b3d0b")
        settings_frame.pack(pady=20)

        # Variant Selection
        StyledLabel(settings_frame, "Game Variant:", size=12).grid(row=0, column=0, padx=10)
        self.variant_var = tk.StringVar(value="Texas Hold'em")
        variant_menu = tk.OptionMenu(self, self.variant_var, "Texas Hold'em", "5-Card Draw", "7-Card Stud")
        variant_menu.config(bg="#2e7d32", fg="white", font=("Arial", 10, "bold"), width=15)
        variant_menu.grid(row=0, column=1, padx=10, in_=settings_frame)

        # Bot Count Selection
        StyledLabel(settings_frame, "Bots:", size=12).grid(row=1, column=0, padx=10, pady=10)
        self.bot_count_spin = tk.Spinbox(settings_frame, from_=1, to=5, width=5, font=("Arial", 12))
        self.bot_count_spin.grid(row=1, column=1, padx=10)


    def confirm_username(self):
        # Save username from input field into StringVar
        self.username_value.set(self.username_entry.get())
        print(f"Username set to: {self.username_value.get()}")

    def singleplayer(self):
        name = self.username_value.get() or "Player"
        variant = self.variant_var.get()
        bot_count = int(self.bot_count_spin.get())
        
        self.start_callback(name, variant, bot_count)

    def multiplayer(self):
        # Placeholder for future multiplayer logic
        print("Multiplayer selected")

    def view_stats(self):
        # Placeholder for stats screen
        print("View stats")

    def exit_app(self):
        # Closes the application
        self.master.quit()
