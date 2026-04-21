"""
**************************************************************************

logic.py is for:

organizing the flow of the game

**************************************************************************
"""


import json
from itertools import combinations
from core.cards import Deck
from core.players import Player
from scoring import Evaluator


class PokerGameLogic:
    def __init__(self, game_state):
        self.state = game_state

    # Add a new player
    def add_player(self, name, chips=1000):
        player = Player(name, chips)
        self.state.players.append(player)


    # Starting a new hand
    def start_hand(self):
        self.state.phase = "pre-flop"
        self.state.pot = 0
        self.state.current_bet_to_match = 0
        self.state.community_cards = []
        self.state.last_action = None
        self.state.action_history = []

        # Reset the deck
        self.state.deck.reset()
        self.state.deck.shuffle()

        # Reset players
        for p in self.state.players:
            p.reset_round_state()

        # Deal 2 cards to each player
        for p in self.state.players:
            p.hand.add_cards(self.state.deck.draw(2))

        # Find the positions of the blinds
        sb_idx = (self.state.dealer_position + 1) % len(self.state.players)
        bb_idx = (self.state.dealer_position + 2) % len(self.state.players)

        # Force the bets (set to 5 and 10 chips for now, might consider doubling mechanism)
        self._handle_bet(self.state.players[sb_idx], 5)
        self._handle_bet(self.state.players[bb_idx], 10)

        # Update the first turn to the person after Big Blind
        self.state.current_turn = (bb_idx + 1) % len(self.state.players)


    # Process the actions from the server
    def process(self, action):
        move = action["action"]
        player_name = action["player_name"]

        player = self.find_player(player_name)

        if move == "deal":
            self.start_hand()

        elif move == "bet":
            amount = action["amount"]
            self.handle_bet(player, amount)

        elif move == "fold":
            self.handle_fold(player)

        elif move == "next_phase":
            self.advance_phase()

        elif move == "showdown":
            self.handle_showdown()

        # Save action
        self.state.last_action = action
        self.state.action_history.append(action)


    # Betting actions
    def handle_bet(self, player, amount):
        actual = player.bet(amount)
        self.state.pot += actual

        if player.current_bet > self.state.current_bet_to_match:
            self.state.current_bet_to_match = player.current_bet


    def handle_fold(self, player):
        player.is_folded = True


    # Phase changes
    def advance_phase(self):
        if self.state.phase == "pre-flop":
            self.state.phase = "flop"
            self.state.community_cards.extend(self.state.deck.draw(3))

        elif self.state.phase == "flop":
            self.state.phase = "turn"
            self.state.community_cards.extend(self.state.deck.draw(1))

        elif self.state.phase == "turn":
            self.state.phase = "river"
            self.state.community_cards.extend(self.state.deck.draw(1))

        elif self.state.phase == "river":
            self.state.phase = "showdown"


    # Showdown phase
    def handle_showdown(self):
        best_scores = []

        for p in self.state.players:
            if p.is_folded:
                continue

            all_cards = p.hand.cards + self.state.community_cards
            best = self.best_five(all_cards)
            best_scores.append((p, best))

        # Determine winner
        winner = max(best_scores, key=lambda x: x[1])
        self.state.winner = winner[0].name

        # Award the pot to the winner
        winner.chips += self.state.pot
        self.state.pot = 0


    # Determine the winner
    def best_five(self, cards):
        best = (0, [])
        for combo in combinations(cards, 5):
            score = Evaluator.get_score(combo)
            if score > best:
                best = score
        return best


    # Helper fn
    def find_player(self, name):
        for p in self.state.players:
            if p.name == name:
                return p
        raise ValueError(f"Player {name} not found")
