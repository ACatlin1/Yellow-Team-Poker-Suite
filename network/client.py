"""
**************************************************************************

client.py is for:

for connecting to the remote server
Attempting to use playit.gg

**************************************************************************
"""

import socket
import json


# Client Side connects to the server
""" Replace these with the "Address" and "Port" from your playit.gg dashboard"""
REMOTE_HOST = "poker-game-123.playit.gg" 
REMOTE_PORT = 12345 

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((REMOTE_HOST, REMOTE_PORT))
    print("Successfully connected to the Poker Server via Playit.gg!")
except Exception as e:
    print(f"Connection failed: {e}")


def send_action(action_type, amount=0):
    action_data = {
        "player_name": "Alice",
        "action": action_type,
        "amount": amount
    }
    # Encode the dictionary as a JSON string and send
    client.send(json.dumps(action_data).encode('utf-8'))