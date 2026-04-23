"""
**************************************************************************

sprites.py is for:

images/icons for cards and chips and anything else we need

**************************************************************************
"""

import os
import tkinter as tk


class SpriteManager:
    def __init__(self):
        # Cache prevents reloading the same image multiple times
        # Important for performance and avoiding Tkinter image issues
        self.cache = {}

    def load_image(self, path):
        # Returns cached image if already loaded
        if path in self.cache:
            return self.cache[path]

        # If file doesn't exist, log and return None
        if not os.path.exists(path):
            print(f"[Missing Image]: {path}")
            return None

        # Load image and store it in cache
        img = tk.PhotoImage(file=path)
        self.cache[path] = img
        return img

    def card_to_filename(self, card):
        # Converts a card object into a filename
        # Example: Ace of Spades -> "ace_of_spades.png"
        return f"{card.rank.lower()}_of_{card.suit.lower()}.png"

    def get_card_image(self, card):
        # Builds full path to a card image and loads it
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, "assets", "cards", self.card_to_filename(card))
        return self.load_image(path)

    def get_card_back(self):
        # Loads the back-of-card image
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, "assets", "cards", "back.png")
        return self.load_image(path)


# Global instance so the same cache is shared everywhere
sprites = SpriteManager()
