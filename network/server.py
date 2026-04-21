"""
**************************************************************************

server.py is for:

This starts and runs the server for the game
Changed from ngrok to playit.gg for persistant urls

**************************************************************************
"""


import socket
import threading
from data.storage import GameState # access to dataclass


class PokerServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []        # List of socket connections
        self.game_state = GameState()
        self.game_logic = PokerGameLogic(self.game_state)
        print(f"Server started on {port}. Waiting for playit.gg traffic...")

    def broadcast(self, message):
        """Send a JSON string to every connected player."""
        for client in self.clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                self.clients.remove(client)

    def handle_client(self, conn, addr):
        """Each player gets their own version of this function running in a thread."""
        print(f"[NEW CONNECTION] {addr} connected.")
        self.clients.append(conn)

        while True:
            try:
                # 1. Receive JSON action from a player
                data = conn.recv(2048).decode('utf-8')
                if not data: break
                
                action = json.loads(data)

                # Update game logic
                self.game_logic.process(action)
                
                # 3. Tell everyone what happened
                self.broadcast(self.game_state.to_json())
            except:
                break

        conn.close()

    def run(self):
        while True:
            conn, addr = self.server.accept()
            # Start a new thread so the server can go back to listening for more players
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    server = PokerServer()
    server.run()
