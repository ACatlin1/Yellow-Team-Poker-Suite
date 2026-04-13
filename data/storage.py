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
class GameAction:
    player_name: str
    action: str
    amount: int = 0

    def __str__(self):
        if self.amount:
            return f"{self.player_name} {self.action} {self.amount}"
        return f"{self.player_name} {self.action}"


@dataclass
class GameState:
    game_type: str = "Texas Holdem"
    phase: str = "pre-flop"
    pot: int = 0
    current_turn: int = 0
    dealer_position: int = 0
    current_bet_to_match: int = 0
    community_cards: list = field(default_factory=list)
    players: list = field(default_factory=list)
    deck: Deck = field(default_factory=Deck)
    last_action: Optional[GameAction] = None
    action_history: list[GameAction] = field(default_factory=list)


class SaveManager:
    
    SAVE_DIR = "saves"
    MAX_SLOTS = 3

    def save(self, state: GameState, slot: int) -> None:
        path = self._slot_path(slot)
        with open(path, "wb") as f:
            pickle.dump(state, f)

    def load(self, slot: int) -> GameState:
        path = self._slot_path(slot)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No save found in slot {slot}")
        with open(path, "rb") as f:
            return pickle.load(f)

    def delete(self, slot: int) -> None:
        path = self._slot_path(slot)
        if os.path.exists(path):
            os.remove(path)

    def slot_exists(self, slot: int) -> bool:
        return os.path.exists(self._slot_path(slot))

    def get_slot_info(self) -> list[tuple[int, bool]]:
        return [(s, self.slot_exists(s)) for s in range(1, self.MAX_SLOTS + 1)]

    def _slot_path(self, slot: int) -> str:
        if not 1 <= slot <= self.MAX_SLOTS:
            raise ValueError(f"Slot must be between 1 and {self.MAX_SLOTS}")
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        return os.path.join(self.SAVE_DIR, f"slot{slot}.pkl")
