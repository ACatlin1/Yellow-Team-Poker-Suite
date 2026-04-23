"""
**************************************************************************

widgets.py is for:

buttons and text boxes used in the GUI (lobby or card table)

**************************************************************************
"""

import tkinter as tk


class StyledButton(tk.Button):
    def __init__(self, master, text, command=None, width=15):
        # Custom button with consistent styling used across the UI
        # Inherits from tk.Button but predefines colors, font, and size
        super().__init__(
            master,
            text=text,
            command=command,   # Function to run when button is clicked
            width=width,
            height=2,
            bg="#2e7d32",      # Dark green background
            fg="white",        # White text
            font=("Arial", 10, "bold"),
            relief="raised"    # Gives a slightly elevated button look
        )


class StyledLabel(tk.Label):
    def __init__(self, master, text, size=12, bold=False):
        # Label with configurable font size and optional bold styling
        font = ("Arial", size, "bold" if bold else "normal")
        super().__init__(master, text=text, font=font)


class StyledEntry(tk.Entry):
    def __init__(self, master):
        # Standard text input field with consistent width and font
        super().__init__(master, width=20, font=("Arial", 12))
