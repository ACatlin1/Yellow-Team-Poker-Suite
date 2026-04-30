"""
**************************************************************************

client.py is for:

for connecting to the remote server
Attempting to use playit.gg

**************************************************************************
"""

import socket
import json
import threading

class PokerClient:
    def __init__(self, host, port, on_update_callback):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_update_callback = on_update_callback # Function to trigger when state changes
        self.connected = False

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            print(f"Successfully connected to the Poker Server at {self.host}:{self.port}!")
            
            # Start the background listening thread so Tkinter doesn't freeze
            thread = threading.Thread(target=self.listen_thread, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def listen_thread(self):
        """Continuously listens for GameState JSON from the server."""
        while self.connected:
            try:
                # 8192 buffer size to ensure we catch the whole game state string
                data = self.client.recv(8192).decode('utf-8')
                if data:
                    self.on_update_callback(data)
            except:
                print("Disconnected from server.")
                self.connected = False
                break

    def send_action(self, action_dict):
        """Send an action to the server."""
        if self.connected:
            self.client.send(json.dumps(action_dict).encode('utf-8'))