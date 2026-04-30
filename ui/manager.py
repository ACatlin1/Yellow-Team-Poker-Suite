"""
**************************************************************************

manager.py is for:

controlling the GUI screens

**************************************************************************
"""

import tkinter as tk
#import random
from data.storage import GameState
from core.logic import PokerGameLogic
from data.database import DatabaseManager
from ui.auth import AuthScreen
from ui.lobby import LobbyScreen
from ui.table import TableScreen
from ui.stats import StatsScreen


class UIManager:
    def __init__(self):
        # Root window setup
        self.root = tk.Tk()
        self.root.title("Poker Suite")

        # Fixed window size for consistent layout
        self.root.geometry("1000x700")
        self.root.resizable(False, False)

        self.root.process_player_action = self.process_player_action

        # Keeps track of the currently active screen
        self.current_screen = None
        self.db = DatabaseManager()

        self.root.show_stats = self.show_stats

        self.show_auth()
        self.root.mainloop()


    def clear(self):
        # Destroys current screen before switching to another
        if self.current_screen:
            self.current_screen.destroy()


    def show_auth(self):
        self.clear()
        self.current_screen = AuthScreen(self.root, self.handle_login, self.handle_register, self.handle_guest)


    def handle_login(self, username, password, status_label):
        if self.db.verify_login(username, password):
            self.username = username
            self.show_lobby()
        else:
            status_label.config(text="Invalid username or password.")


    def handle_register(self, username, password, status_label):
        if len(username) < 5 or len(password) < 5:
            status_label.config(text="Username and password must be 5+ characters.")
            return

        if self.db.register_player(username, password):
            self.username = username
            self.show_lobby()
        else:
            status_label.config(text="Username already exists.")


    def handle_guest(self):
        self.username = "Guest"
        self.show_lobby()


    def show_lobby(self):
        # Displays lobby screen
        self.clear()
        self.current_screen = LobbyScreen(
            self.root, 
            self.db,
            self.username,
            self.start_game)
        
        self.current_screen.pack(fill="both", expand=True)


    def show_stats(self):
        self.clear()

        stats_data = self.db.get_player_stats(self.username)
        if not stats_data:
            # Mainly used for guest accounts
            stats_data = {"username": self.username, "chips": 1000, "games_played": 0, "games_won": 0}
        else:
            # Get the user stats
            stats_data["username"] = self.username

        self.current_screen = StatsScreen(self.root, stats_data, self.show_lobby)


    def start_game(self, variant_name, bot_count, is_multiplayer=False, load_saved=False):
        """Modified to support fresh starts and loading from DB"""
        print(f"Starting {variant_name} (Load: {load_saved}) for {self.username}")
        self.is_multiplayer = is_multiplayer

        if not self.is_multiplayer:
            self.game_state = GameState()
            self.logic = PokerGameLogic(self.game_state)

            if load_saved:
                saved_state = self.db.get_saved_game(self.username)
                if saved_state:
                    self.game_state = saved_state
                    self.logic = PokerGameLogic(self.game_state)
                    self.logic.set_variant(self.game_state.variant_name)
                    self.show_table()
                    return
                
            else:
                # Fresh start
                self.logic.set_variant(variant_name)
                self.logic.add_player(self.username, is_cpu=False)
                for i in range(bot_count):
                    self.logic.add_player(f"CPU_{i+1}", chips=1000, is_cpu=True)
                
                self.logic.start_hand()

            self.show_table()
            self.refresh_ui()

            # Handle the first turn
            first_player = self.game_state.players[self.game_state.current_turn]
            if first_player.is_cpu:
                self.root.after(1500, self.trigger_bot_move)

        else:
            """Online Mode"""
            from network.client import PokerClient
            
            # Initialize a blank state until the server sends the real one
            self.game_state = GameState() 
            self.show_table()

            # Connect to the server
            playit_url = "approve-ministries.with.playit.plus"
            playit_port = 1093

            self.network_client = PokerClient(playit_url, playit_port, self.on_network_update)
            success = self.network_client.connect()

            if success:
                # Send a join request immediately
                self.network_client.send_action({
                    "action": "join",
                    "player_name": self.username
                })
            else:
                # Return to the lobby screen
                print("Failed to connect to multiplayer. Returning to lobby.")
                self.show_lobby()


    def show_table(self):
        """Updated to touch the game state"""
        # Displays main table screen
        self.clear()
        self.current_screen = TableScreen(
            self.root, 
            self, 
            self.show_lobby, 
            self.game_state, 
            self.username
            )
        
        self.current_screen.pack(fill="both", expand=True)


    def show_pause_menu(self):
        """Creates a Toplevel popup to pause the game."""
        pause_win = tk.Toplevel(self.root)
        pause_win.title("Paused")
        pause_win.geometry("300x250")
        pause_win.configure(bg="#2c3e50")
        
        # Block interaction with the main window
        pause_win.grab_set()

        tk.Label(pause_win, text="GAME PAUSED", fg="white", bg="#2c3e50", 
                 font=("Arial", 16, "bold")).pack(pady=20)

        # Resume just kills the popup
        tk.Button(pause_win, text="Resume", width=15, 
                  command=pause_win.destroy).pack(pady=10)

        # Save & Exit triggers the DB save and goes to lobby
        tk.Button(pause_win, text="Save & Exit", width=15, 
                  command=lambda: self.save_and_quit(pause_win)).pack(pady=10)
        

    def refresh_ui(self):
        """Adding to clarify refreshing the visual updates"""

        # Block refresh if we're not on the right screen
        if not isinstance(self.current_screen, TableScreen):
            return

        # Update Pot
        self.current_screen.update_pot(self.game_state.pot)

        # Update Community Cards
        self.current_screen.render_community(self.game_state.community_cards)

        # Update Player Hand
        human = None
        for p in self.game_state.players:
            if p.name == self.username:
                human = p
                break
                
        # If the server hasn't added us to the state yet, pause the render
        if not human:
            return
        self.current_screen.render_player_hand(human.hand.cards)
        
        if self.game_state.phase == "draw":
            if hasattr(self.current_screen, 'selected_discards') and len(self.current_screen.selected_discards) > 0:
                self.current_screen.check_call_btn.config(text="Discard Selected")
            else:
                self.current_screen.check_call_btn.config(text="Stand Pat (Keep All)")
                
        elif self.game_state.phase == "showdown":
            self.current_screen.check_call_btn.config(text="Next Hand")
            
        else:
            to_call = self.game_state.current_bet_to_match - human.current_bet
            self.current_screen.update_check_call(to_call)

        # Update Opponents
        # Get everyone EXCEPT the human player
        opponents = [p.hand.cards for p in self.game_state.players if p.name != self.username]
        self.current_screen.render_opponents(opponents)

        if self.game_state.phase == "showdown":
            self.current_screen.check_call_btn.config(text="Next Hand")
        
        elif self.game_state.phase == "draw":
            if hasattr(self.current_screen, 'selected_discards') and len(self.current_screen.selected_discards) > 0:
                self.current_screen.check_call_btn.config(text="Discard Selected")
            else:
                self.current_screen.check_call_btn.config(text="Stand Pat (Keep All)")
    

    def trigger_bot_move(self):
        
        if self.game_state.phase in ["showdown", "end"]:
            return
        
        active_player = self.game_state.players[self.game_state.current_turn]

        if active_player.name == self.username or not active_player.is_cpu:
            return  

        bot_action = self.logic.take_bot_action()

        if bot_action:
            self.logic.process(bot_action)
            self.refresh_ui()

            # Only trigger next bot if turn actually changed
            next_player = self.game_state.players[self.game_state.current_turn]

            if next_player.is_cpu and self.game_state.phase not in ["showdown", "end"]:
                self.root.after(1500, self.trigger_bot_move)


    """def take_bot_action(self):
        ""Determine if the current player is a bot and executes the move.""
        
        current_player = self.state.players[self.state.current_turn]
        
        if current_player.is_cpu and not current_player.is_folded:
            ai = BotAI()
            random_action = random.randint(1,20)

            if random_action >= 11:
                action = ai.choose_action(current_player, self.state)
            elif random_action >= 5:
                action = ai.choose_action(current_player, self.state)
            else:    
                action = ai.choose_action(current_player, self.state)

            self.process(self.translate_bot_action(action))

            return action
        return None
    
    def translate_bot_action(self, action):
        player = self.state.players[self.state.current_turn]
        to_call = self.state.current_bet_to_match - player.current_bet

        if action["action"] == "bet":
            return {
                "player_name": player.name,
                "action": "bet",
                "amount": max(action["amount"], to_call)
            }

        return action"""


    def process_player_action(self, action_dict):
        
        #****************************************************************
        #Debug statement
        print(f"UI Button Clicked: {action_dict}")
        #****************************************************************

        # Identify the Human Player
        human = None
        for p in self.game_state.players:
            if p.name == self.username:
                human = p
                break
        if not human:
            return

        action = action_dict.get("action", "")

        if action == "pause":
            print("[UI] Game Paused")
            self.show_pause_menu()
            return

        # Automatically push Next Round clicks through if the round ends early
        if self.game_state.phase in ["showdown", "end"] or action in ["next_round", "next_hand", "new_hand"]:
            if self.is_multiplayer:
                self.network_client.send_action({"action": "next_hand"})
            else:
                self.logic.start_hand()
                self.refresh_ui()
                
                # Check if the bot happens to be the dealer/first-actor on the new hand
                first_player = self.game_state.players[self.game_state.current_turn]
                if first_player.name != self.username and first_player.is_cpu:
                    self.root.after(1500, self.trigger_bot_move)
            return

        # Stop any actions outside of players turn
        active_player = self.game_state.players[self.game_state.current_turn]
        if active_player.name != self.username:
            print("Please wait, it is not your turn!")
            return

        # Translate UI actions to Logic actions
        to_call = self.game_state.current_bet_to_match - human.current_bet
        
        if self.game_state.phase == "draw":
            discard_indices = list(self.current_screen.selected_discards)
            translated = {
                "player_name": human.name,
                "action": "discard",
                "indices": discard_indices
            }
        elif action == "check":
            translated = { "player_name": human.name, 
                          "action": "bet", 
                          "amount": 0 }
        elif action == "call":
            translated = { "player_name": human.name, 
                          "action": "bet", 
                          "amount": max(to_call, 0) }
        elif action == "raise":
            translated = { "player_name": human.name, 
                          "action": "bet", 
                          "amount": to_call + action_dict.get("amount", 50) }
        elif action == "fold":
            translated = { "player_name": human.name, 
                          "action": "fold", 
                          "amount": 0 }
        else:
            print(f"Unknown UI action: {action}")
            return

        # Route the translated action
        if self.is_multiplayer:
            self.network_client.send_action(translated)
        else:
            self.logic.process(translated)
            self.refresh_ui()

            # Trigger bot ONLY if the hand is still actively playing
            next_player = self.game_state.players[self.game_state.current_turn]
            if next_player.is_cpu and self.game_state.phase not in ["showdown", "end"]:
                self.root.after(1500, self.trigger_bot_move)


    def on_network_update(self, json_string):

        """Called by the client.py background thread when the server broadcasts."""
        # Read the JSON string back into a GameState object
        self.game_state = GameState.from_json(json_string)
        
        # Tell Tkinter's main thread to refresh the screen
        self.root.after(0, self.refresh_ui)


    def save_and_quit(self, popup):
        """Serializes the current GameState and saves to DB."""
       # Save to  DatabaseManager
        self.db.save_game_state(self.username, self.game_state)
        
        popup.destroy()
        self.show_lobby()
        