"""
**************************************************************************

stats.py is for:

A new screen for displaying user stats

**************************************************************************
"""

import tkinter as tk
from ui.widgets import StyledButton, StyledLabel

class StatsScreen(tk.Frame):
    def __init__(self, master, stats_data, back_callback):
        super().__init__(master)
        self.stats = stats_data  # Dictionary containing chip/win data
        self.back_callback = back_callback

        self.pack(fill="both", expand=True)
        self.configure(bg="#0b3d0b")

        self.build()

    def build(self):
        center = tk.Frame(self, bg="#0b3d0b")
        center.place(relx=0.5, rely=0.5, anchor="center")

        StyledLabel(center, f"Career Stats for {self.stats.get('username', 'Player')}", size=24, bold=True).pack(pady=20)

        # Display Stats
        StyledLabel(center, f"Total Chips: ${self.stats.get('chips', 0)}", size=16).pack(pady=5)
        StyledLabel(center, f"Hands Played: {self.stats.get('games_played', 0)}", size=16).pack(pady=5)
        StyledLabel(center, f"Hands Won: {self.stats.get('games_won', 0)}", size=16).pack(pady=5)

        # Calculate win rate safely
        played = self.stats.get('games_played', 0)
        won = self.stats.get('games_won', 0)
        win_rate = (won / played * 100) if played > 0 else 0
        StyledLabel(center, f"Win Rate: {win_rate:.1f}%", size=16).pack(pady=5)

        StyledButton(center, "Back to Lobby", self.back_callback).pack(pady=30)