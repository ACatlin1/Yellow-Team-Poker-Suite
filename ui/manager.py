"""
**************************************************************************

manager.py is for:

controlling the GUI screens

**************************************************************************
"""

import tkinter as tk
from ui.lobby import LobbyScreen
from ui.table import TableScreen


class UIManager:
    def __init__(self):
        # Root window setup
        self.root = tk.Tk()
        self.root.title("Poker Suite")

        # Fixed window size for consistent layout
        self.root.geometry("1000x700")
        self.root.resizable(False, False)

        # Keeps track of the currently active screen
        self.current_screen = None

        # Start with lobby screen
        self.show_lobby()

        # Begin Tkinter event loop
        self.root.mainloop()

    def clear(self):
        # Destroys current screen before switching to another
        if self.current_screen:
            self.current_screen.destroy()

    def show_lobby(self):
        # Displays lobby screen
        self.clear()
        self.current_screen = LobbyScreen(self.root, self.start_game)

    def start_game(self, username):
        # Entry point for starting a game
        print(f"Starting game for {username}")
        self.show_table()

    def show_table(self):
        # Displays main table screen
        self.clear()
        self.current_screen = TableScreen(self.root)

    def show_table(self):
        self.clear()
        self.current_screen = TableScreen(self.root, self.show_lobby)
