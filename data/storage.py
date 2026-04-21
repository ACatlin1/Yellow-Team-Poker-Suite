"""
**************************************************************************

storage.py is for:

This is for game states.
We will use both pickle and JSON to save game files.
Pickle worked well for local states.
But JSON worked better for server communication.

**************************************************************************
"""

import os
import pickle
from dataclasses import dataclass, field
from typing import Optional
from core.cards import Deck
import json
from dataclasses import asdict

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
    phase: str = "pre-flop"             # current phase: pre-flop, flop, turn, river, showdown
    pot: int = 0                        # total chips in the pot
    current_turn: int = 0               # index of the player whose turn it is
    dealer_position: int = 0            # index of the current dealer
    current_bet_to_match: int = 0       # the highest bet players must match to stay in
    community_cards: list = field(default_factory=list)             # shared cards on the table
    players: list = field(default_factory=list)                     # list of Player objects
    deck: Deck = field(default_factory=Deck)                        # the active deck
    last_action: Optional[GameAction] = None                        # most recent action taken
    action_history: list[GameAction] = field(default_factory=list)  # full log of actions this round

    def to_json(self) -> str:
        """Converts the current state into a JSON string for networking.
            asdict converts the dataclass and nested objects into a dict"""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        """Creates a GameState object from a received JSON string."""
        data = json.loads(json_str)
        return cls(**data)


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
        [(1, True), (2, False), (3, True)]
        return [(s, self.slot_exists(s)) for s in range(1, self.MAX_SLOTS + 1)]

    def _slot_path(self, slot: int) -> str:
        
        if not 1 <= slot <= self.MAX_SLOTS:
            raise ValueError(f"Slot must be between 1 and {self.MAX_SLOTS}")
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        return os.path.join(self.SAVE_DIR, f"slot{slot}.pkl")
