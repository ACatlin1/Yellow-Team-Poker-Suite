"""
**************************************************************************

server.py is for:

This starts and runs the server for the game
Changed from ngrok to playit.gg for persistant urls

**************************************************************************
"""


import socket
import threading
import json
from data.storage import GameState
from core.logic import PokerGameLogic

class PokerServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []        
        self.game_state = GameState()
        self.game_logic = PokerGameLogic(self.game_state)
        print(f"Server started on port {port}. Waiting for players...")

    def broadcast(self):
        """Send the current GameState JSON string to every connected player."""
        try:
            state_json = self.game_state.to_json() + "\n"
            for client in self.clients:
                try:
                    client.send(state_json.encode('utf-8'))
                except:
                    self.clients.remove(client)
        except Exception as e:
            print(f"JSON Serialization Error: {e}")

    def handle_client(self, conn, addr):
        """Each player gets their own thread."""
        print(f"[NEW CONNECTION] {addr} connected.")
        self.clients.append(conn)
        player_name = None

        while True:
            try:
                # Receive JSON action from a player
                data = conn.recv(2048).decode('utf-8')
                if not data: break
                
                action = json.loads(data)

                # Check if this is a connection action or a game action
                if action["action"] == "join":
                    self.game_logic.add_player(action["player_name"], is_cpu=False)
                    print(f"[Lobby] {action['player_name']} joined the game.")
                    
                    # If this is the first player, just set the rules and wait
                    if len(self.game_state.players) == 1:
                        self.game_logic.set_variant("Texas Hold'em") 
                        print("[Server] Host joined. Waiting for opponents...")
                    
                    # Once a second player joins, deal!
                    elif len(self.game_state.players) == 2:
                        self.game_logic.start_hand()
                        print("[Server] Second player joined. Starting hand!")
                else:
                    self.game_logic.process(action)
                
                # Tell everyone what happened
                self.broadcast()
            except Exception as e:
                print(f"Error with {addr}: {e}")
                break

        print(f"[DISCONNECTED] {addr}")
        if conn in self.clients:
            self.clients.remove(conn)

        if player_name:
            self.game_state.players = [p for p in self.game_state.players if p.name != player_name]
            print(f"[Server] Removed ghost player: {player_name}")
            self.broadcast()
            
        conn.close()

    def run(self):
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    server = PokerServer()
    server.run()