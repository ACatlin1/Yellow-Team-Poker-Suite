"""
**************************************************************************

storage.py is for:

this will be for game states.
We will likely use either pickle or JSON to save game files.

**************************************************************************
"""

import os
import pickle
from dataclasses import dataclass, field
from typing import Optional
from core.cards import Deck


@dataclass
class SlotInfo:
    slot: int
    occupied: bool


@dataclass
class GameAction:
    player_name: str
    action: str
    amount: int = 0

    def __str__(self):
        if self.amount:
            return f"{self.player_name} {self.action} {self.amount}"
        return f"{self.player_name} {self.action}"


PHASES = ["pre-flop", "flop", "turn", "river", "showdown"]


class GameStateError(Exception):
    pass


class GameState:
    
    SAVE_DIR = "saves"
    MAX_SLOTS = 3

    def __init__(self, players=None, game_type="Texas Holdem"):
        self.game_type = game_type
        self.players = players if players is not None else []

        self.deck = Deck()
        self.deck.shuffle()

        self.phase = "pre-flop"
        self.pot = 0
        self.current_turn = 0
        self.dealer_position = 0
        self.current_bet_to_match = 0
        self.community_cards = []
        self.last_action: Optional[GameAction] = None
        self.action_history: list[GameAction] = []

    
    # Dealing                                                              
    
    
    def deal_to_player(self, player_index: int, num_cards: int = 1) -> None:
        self._validate_player_index(player_index)
        drawn = self.deck.draw(num_cards)
        self.players[player_index].hand.add_cards(drawn)

    def deal_to_all_players(self, num_cards: int = 1) -> None:
        for i, _ in enumerate(self.players):
            self.deal_to_player(i, num_cards)

    def deal_community(self, num_cards: int = 1) -> None:
        drawn = self.deck.draw(num_cards)
        self.community_cards.extend(drawn)

   
    # Player actions                                                       


    def place_bet(self, player_index: int, amount: int) -> int:
        self._validate_player_index(player_index)
        player = self.players[player_index]
        actual_bet = player.bet(amount)
        self.pot += actual_bet

        if player.current_bet > self.current_bet_to_match:
            self.current_bet_to_match = player.current_bet

        self._record_action(GameAction(player.name, "bet", actual_bet))
        return actual_bet

    def fold_player(self, player_index: int) -> None:
        self._validate_player_index(player_index)
        player = self.players[player_index]
        player.is_folded = True
        self._record_action(GameAction(player.name, "fold"))

    def check_player(self, player_index: int) -> None:
        self._validate_player_index(player_index)
        player = self.players[player_index]
        self._record_action(GameAction(player.name, "check"))

    def call_player(self, player_index: int) -> int:
        self._validate_player_index(player_index)
        player = self.players[player_index]
        amount_needed = max(0, self.current_bet_to_match - player.current_bet)
        actual_bet = player.bet(amount_needed)
        self.pot += actual_bet
        self._record_action(GameAction(player.name, "call", actual_bet))
        return actual_bet

    def raise_player(self, player_index: int, raise_amount: int) -> int:
        self._validate_player_index(player_index)

        if raise_amount < self.current_bet_to_match:
            raise GameStateError(
                f"Raise amount ({raise_amount}) must be at least the size "
                f"of the current bet ({self.current_bet_to_match})"
            )

        player = self.players[player_index]
        amount_needed = max(0, self.current_bet_to_match - player.current_bet)
        total_amount = amount_needed + raise_amount
        actual_bet = player.bet(total_amount)
        self.pot += actual_bet

        if player.current_bet > self.current_bet_to_match:
            self.current_bet_to_match = player.current_bet

        self._record_action(GameAction(player.name, "raise", actual_bet))
        return actual_bet

    
    # Turn / phase management                                              
    

    def next_turn(self) -> bool:
        if not self.players:
            return False

        num_players = len(self.players)
        for _ in range(num_players):
            self.current_turn = (self.current_turn + 1) % num_players
            player = self.players[self.current_turn]
            if not player.is_folded and not player.is_all_in:
                return True

        return False

    def advance_phase(self) -> None:
        try:
            idx = PHASES.index(self.phase)
        except ValueError:
            raise GameStateError(f"Unknown phase: {self.phase!r}")

        if idx == len(PHASES) - 1:
            raise GameStateError("Already at showdown — cannot advance phase")

        self.phase = PHASES[idx + 1]

    def reset_bets_for_new_phase(self) -> None:
        self.current_bet_to_match = 0
        for player in self.players:
            player.current_bet = 0

    def reset_round(self) -> None:
        self.deck = Deck()
        self.deck.shuffle()
        self.phase = "pre-flop"
        self.pot = 0
        self.current_bet_to_match = 0
        self.community_cards = []
        self.last_action = None
        self.action_history = []

        if self.players:
            self.dealer_position = (self.dealer_position + 1) % len(self.players)
            self.current_turn = self.dealer_position

        for player in self.players:
            player.reset_round_state()

   
    # Save / load                                                          
   

    def save_to_slot(self, slot: int) -> None:
        path = self._slot_path(slot)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_from_slot(cls, slot: int) -> "GameState":
        path = cls._slot_path(slot)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No save found in slot {slot}")
        with open(path, "rb") as f:
            return pickle.load(f)

    @classmethod
    def slot_exists(cls, slot: int) -> bool:
        return os.path.exists(cls._slot_path(slot))

    @classmethod
    def delete_slot(cls, slot: int) -> None:
        cls._validate_slot(slot)
        path = cls._slot_path(slot)
        if os.path.exists(path):
            os.remove(path)

    @classmethod
    def get_slot_info(cls) -> list[SlotInfo]:
        return [SlotInfo(s, cls.slot_exists(s)) for s in range(1, cls.MAX_SLOTS + 1)]

    
    # Internal helpers                                                   
    

    def _record_action(self, action: GameAction) -> None:
        self.last_action = action
        self.action_history.append(action)

    def _validate_player_index(self, index: int) -> None:
        if not 0 <= index < len(self.players):
            raise GameStateError(f"Invalid player index: {index}")

    @classmethod
    def _validate_slot(cls, slot: int) -> None:
        if not 1 <= slot <= cls.MAX_SLOTS:
            raise ValueError(f"Slot must be between 1 and {cls.MAX_SLOTS}")

    @classmethod
    def _slot_path(cls, slot: int) -> str:
        cls._validate_slot(slot)
        os.makedirs(cls.SAVE_DIR, exist_ok=True)
        return os.path.join(cls.SAVE_DIR, f"slot{slot}.pkl")

    def __repr__(self) -> str:
        return (
            f"<GameState phase={self.phase!r} pot={self.pot} "
            f"players={len(self.players)} turn={self.current_turn}>"
        )
