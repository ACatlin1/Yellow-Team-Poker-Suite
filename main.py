import threading
import time
from core.cards import Deck
from core.players import Player
from ui.manager import UIManager
from network.server import PokerServer


# Start the server on launch
def start_background_server():
    try:
        # Attempt to start the server on port 5555
        server = PokerServer(host='0.0.0.0', port=5555)
        server.run()
    except OSError:
        # Catch the error if you accidently launch twice. The port will already be in use.
        print("[System] Server is already running in another instance.")


# Start the server on a background daemon thread - exits automatically when the program ends
server_thread = threading.Thread(target=start_background_server, daemon=True)
server_thread.start()


# Give the server a recommended half-second to fully boot and bind to the port
time.sleep(0.5)


# Launch the main UI
UIManager()