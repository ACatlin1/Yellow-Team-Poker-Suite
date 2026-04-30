"""
**************************************************************************

logic.py is for:

organizing the flow of the game

**************************************************************************
"""


import json
from core.cards import Deck
from core.players import Player
from core.scoring import Evaluator, best_five


class PokerGameLogic:
    def __init__(self, game_state):
        self.state = game_state


    # Choose the game type
    def set_variant(self, variant_name):
        """Bridges core logic with variant-specific rules."""
        self.state.variant_name = variant_name
        
        if variant_name == "Texas Hold'em":
            from variants.holdem import TexasHoldem
            self.rules = TexasHoldem(
                self.state.players,
                self.state.deck,
                self.state.community_cards
            )

        elif variant_name == "5-Card Draw":
            from variants.draw import Draw
            self.rules = Draw(
                self.state.players,
                self.state.deck
            )

        elif variant_name == "7-Card Stud":
            from variants.stud import Stud
            self.rules = Stud(
                self.state.players,
                self.state.deck
        )


    # Add a new player
    def add_player(self, name, chips=1000, is_cpu=False):
        player = Player(name, chips, is_cpu=is_cpu)
        self.state.players.append(player)
        if is_cpu:
            print(f"[Lobby] Added CPU Player: {name}")


    # Starting a new hand
    def start_hand(self):
        self.state.phase = "pre-flop"
        self.state.pot = 0
        self.state.community_cards.clear()
        self.state.deck.reset()
        self.state.deck.shuffle()

        # Reset the state of each player
        for p in self.state.players:
            p.hand.cards.clear()
            p.current_bet = 0
            p.is_folded = False
            p.is_all_in = False

        # Reset betting round tracking
        self.state.actions_this_round = 0
        self.state.current_bet_to_match = 0

        # Deal cards based on the selected rules
        self.rules.deal_initial_cards()

        # Handle blinds
        sb = self.rules.small_blind
        bb = self.rules.large_blind

        # Appoint who has each blind
        self.state.players[0].bet(sb)
        self.state.players[1].bet(bb)

        # Add the blinds to the pot
        self.state.pot += sb + bb
        self.state.current_bet_to_match = bb

        # Player after BB acts first
        self.state.current_turn = 2 % len(self.state.players)


    # Process the actions from the server
    def process(self, action):
        """
        Switchboard for the possible moves
        """

        move = action["action"]
        player_name = action["player_name"]

        player = self.find_player(player_name)

        if move == "deal":
            self.start_hand()

        elif move == "check":
            self.handle_bet(player, 0)
            self.state.actions_this_round += 1
            self.advance_turn()

        elif move == "bet":
            amount = action["amount"]
            self.handle_bet(player, amount)
            self.state.actions_this_round += 1
            self.advance_turn()

        elif move == "fold":
            self.handle_fold(player)
            self.state.actions_this_round += 1
            self.advance_turn()
        
        elif move == "discard":
            indices = action.get("indices", [])
            # Only attempt to draw if the current variant is 'Draw'
            if hasattr(self.rules, 'discard_and_draw'):
                self.rules.discard_and_draw(player, indices)
            
            self.state.actions_this_round += 1
            self.advance_turn()

        elif move == "next_phase":
            self.advance_phase()
            self.advance_turn()

        # Save action
        self.state.last_action = action
        self.state.action_history.append(action)

        #********************************************************************************
        # Prints in the terminal to follow backend action and processing.
        print("---- DEBUG STATE ----")
        print("Phase:", self.state.phase)
        print("Turn:", self.state.current_turn)
        print("Actions this round:", self.state.actions_this_round)
        print("Current bet to match:", self.state.current_bet_to_match)
        for p in self.state.players:
            print(f"{p.name}: bet={p.current_bet}, folded={p.is_folded}, chips={p.chips}")
        print("----------------------")
        #********************************************************************************


        # Check for early end. If all others fold, the game ends early
        active_players = [p for p in self.state.players if not p.is_folded]
        
        if len(active_players) == 1:
            if self.state.phase != "showdown":
                self.state.phase = "showdown"  # This triggers the end-of-hand UI state
                winner = active_players[0]
                self.state.winner = winner.name
                winner.chips += self.state.pot
                self.state.pot = 0
                print(f"[Win] {winner.name} wins the pot by default!")
            return
        
        # Modified to address an infin loop in during showdown
        if self.state.phase != "showdown" and self.is_betting_round_over():
            self.advance_phase()


    # Betting mecahincs
    def handle_bet(self, player, amount):

        # A straigjt up bet on your turn
        actual = player.bet(amount)
        self.state.pot += actual

        # If you try to bet, but another has already raised the pot, you match it
        if player.current_bet > self.state.current_bet_to_match:
            self.state.current_bet_to_match = player.current_bet


    # Find the end of the round
    def is_betting_round_over(self):
        active = [p for p in self.state.players if not p.is_folded]

        # If only one player remains, round is over
        if len(active) <= 1:
            return True
        
        # Handle draw logic since it's a "special action" for 'Draw" game type
        if self.state.phase == "draw":
            return self.state.actions_this_round >= len(active)

        # Everyone must have acted at least once
        if self.state.actions_this_round < len(active):
            return False

        # Everyone must have matched the current bet
        return all(
            p.current_bet == self.state.current_bet_to_match
            for p in active
        )


    # Folding action
    def handle_fold(self, player):
        player.is_folded = True


    # Phase changes - or advancing to a new kind of round
    def advance_phase(self):
        for p in self.state.players:
            p.current_bet = 0

        self.state.current_bet_to_match = 0
        self.state.actions_this_round = 0

        variant_type = self.rules.__class__.__name__

        # Hold Em game type
        if variant_type == "TexasHoldem":
            if self.state.phase == "pre-flop":
                self.state.phase = "flop"
                self.rules.deal_community_cards(3)
                self.state.community_cards = self.rules.community_cards

            elif self.state.phase == "flop":
                self.state.phase = "turn"
                self.rules.deal_community_cards(1)
                self.state.community_cards = self.rules.community_cards

            elif self.state.phase == "turn":
                self.state.phase = "river"
                self.rules.deal_community_cards(1)
                self.state.community_cards = self.rules.community_cards

            elif self.state.phase == "river":
                self.state.phase = "showdown"
                self.handle_showdown()

        # Draw game type
        elif variant_type == "Draw":
            if self.state.phase == "pre-flop":
                self.state.phase = "draw"
                
            elif self.state.phase == "draw":
                self.state.phase = "post-draw"
                
            elif self.state.phase == "post-draw":
                self.state.phase = "showdown"
                self.handle_showdown()
        
        # Stud game type
        elif variant_type == "Stud":
            if self.state.phase == "pre-flop":
                self.state.phase = "fourth-street"
                self.rules.deal_street_card(face_up=True)

            elif self.state.phase == "fourth-street":
                self.state.phase = "fifth-street"
                self.rules.deal_street_card(face_up=True)

            elif self.state.phase == "fifth-street":
                self.state.phase = "sixth-street"
                self.rules.deal_street_card(face_up=True)

            elif self.state.phase == "sixth-street":
                self.state.phase = "seventh-street"
                self.rules.deal_street_card(face_up=False) # River card is face down

            elif self.state.phase == "seventh-street":
                self.state.phase = "showdown"
                self.handle_showdown()


    # Showdown phase
    def handle_showdown(self):

        for p in self.state.players:
            for c in p.hand.cards:
                c.is_face_up = True
                
        best_scores = []

        for p in self.state.players:
            if p.is_folded:
                continue

            all_cards = p.hand.cards + self.state.community_cards
            best = best_five(all_cards)
            best_scores.append((p, best))

        # Determine winner
        winner = max(best_scores, key=lambda x: x[1])
        self.state.winner = winner[0].name

        # Award the pot to the winner
        winner_player = winner[0]
        winner_player.chips += self.state.pot

        self.state.pot = 0


    # Helper fn to target a certain player
    def find_player(self, name):
        for p in self.state.players:
            if p.name == name:
                return p
        raise ValueError(f"Player {name} not found")


    # Randomize a bot's action
    def take_bot_action(self):
        """Determine if the current player is a bot and executes the move."""
        from core.npc import BotAI 
        
        # Get the player whose turn it currently is
        current_player = self.state.players[self.state.current_turn]
        
        # Only allow if it's actually a CPU player and they haven't folded
        if current_player.is_cpu and not current_player.is_folded:
            ai = BotAI()
            
            # Use the 'low-tech' randomization "AI" call
            action = ai.choose_action(current_player, self.state)
            
            # Process the bot's choice through the standard game engine
            return self.translate_bot_action(action)
            
        return None
    

    # Handle the bot's betting
    def translate_bot_action(self, action):
        player = self.state.players[self.state.current_turn]
        to_call = self.state.current_bet_to_match - player.current_bet

        if action["action"] == "bet":
            # Treat the bot "bet" as call unless it exceeds the call amount
            return {
                "player_name": player.name,
                "action": "bet",
                "amount": max(action["amount"], to_call)
            }

        return action


    # Push through a round
    def advance_turn(self):
        """Moves the turn to the next active player, skipping anyone who folded."""
        self.state.current_turn = (self.state.current_turn + 1) % len(self.state.players)
        
        # Prevent an infinite loop if everyone folds
        active_players = sum(1 for p in self.state.players if not p.is_folded)
        
        if active_players > 1:
            # Keep advancing until we land on someone who hasn't folded
            while self.state.players[self.state.current_turn].is_folded:
                self.state.current_turn = (self.state.current_turn + 1) % len(self.state.players)