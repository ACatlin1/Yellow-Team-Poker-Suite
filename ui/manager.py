"""
**************************************************************************

manager.py is for:

controlling the GUI screens

**************************************************************************
"""

import tkinter as tk
import random
from data.storage import GameState
from core.logic import PokerGameLogic
from core.npc import BotAI
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

    def start_game(self, username, variant_name, bot_count):
        """Updated to start a true intsnace of the game"""
        print(f"Starting {variant_name} with {bot_count} bots for {username}")

        # Create a fresh GameState
        self.game_state = GameState()

        # Create the logic engine
        self.logic = PokerGameLogic(self.game_state)

        # Set the game variant
        self.logic.set_variant(variant_name)

        # Add the human player
        self.logic.add_player(username, is_cpu=False)

        # Add a bot opponents
        for i in range(bot_count):
            self.logic.add_player(f"CPU_{i+1}", chips=1000)
            self.game_state.players[-1].is_cpu = True

        # Start the first hand
        self.logic.set_variant(variant_name)
        self.logic.start_hand()

        # Show the table screen
        self.show_table()

        # Render everything
        self.refresh_ui()

        # Start action if a bot has the first move in a round
        first_player = self.game_state.players[self.game_state.current_turn]
        if first_player.is_cpu:
            self.root.after(1500, self.trigger_bot_move)


    def show_table(self):
        """Updated to touch the game state"""
        # Displays main table screen
        self.clear()
        self.current_screen = TableScreen(self.root, self, self.show_lobby, self.game_state)


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
        # (Assuming the first player in the list is the human - I need to double check this *********)
        human = self.game_state.players[0]
        self.current_screen.render_player_hand(human.hand.cards)
        to_call = self.game_state.current_bet_to_match - human.current_bet
        self.current_screen.update_check_call(to_call)

        # Update Opponents
        # Get everyone EXCEPT the human player
        opponents = [p.hand.cards for p in self.game_state.players[1:]]
        self.current_screen.render_opponents(opponents)

        if self.game_state.phase == "showdown":
            self.current_screen.check_call_btn.config(text="Next Hand")
    

    def trigger_bot_move(self):
        
        # Block bot actions during showdown
        if self.game_state.phase == "showdown":
            return

        bot_action = self.logic.take_bot_action()

        if bot_action:
            self.refresh_ui()

            # Only trigger next bot if turn actually changed
            next_player = self.game_state.players[self.game_state.current_turn]

            if next_player.is_cpu and not next_player.is_folded:
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
        """Translate UI actions into logic.py actions."""

        if self.game_state.phase == "showdown":
            self.logic.start_hand()
            self.refresh_ui()
            
            # If a bot is supposed to act first in the new hand, start it
            first_player = self.game_state.players[self.game_state.current_turn]
            if first_player.is_cpu:
                self.root.after(1500, self.trigger_bot_move)
            return
        
        # Guard added to prevent butotn pushing when it's not your turn
        if self.game_state.current_turn != 0:
            print("Please wait, it is not your turn!")
            return

        player = self.game_state.players[0]
        to_call = self.game_state.current_bet_to_match - player.current_bet

        action = action_dict["action"]
        player = self.game_state.players[0]
        to_call = self.game_state.current_bet_to_match - player.current_bet

        action = action_dict["action"]

        # Translate UI actions → logic actions
        if action == "check":
            translated = {
                "player_name": player.name,
                "action": "bet",
                "amount": 0
            }

        elif action == "call":
            translated = {
                "player_name": player.name,
                "action": "bet",
                "amount": max(to_call, 0)
            }

        elif action == "raise":
            translated = {
                "player_name": player.name,
                "action": "bet",
                "amount": to_call + action_dict.get("amount", 50)
            }

        elif action == "fold":
            translated = {
                "player_name": player.name,
                "action": "fold",
                "amount": 0
            }

        else:
            print("Unknown UI action:", action)
            return

        # Process through logic engine
        self.logic.process(translated)
        self.refresh_ui()

        # If next player is a bot, trigger bot move
        next_player = self.game_state.players[self.game_state.current_turn]
        if next_player.is_cpu:
            self.root.after(1500, self.trigger_bot_move)
