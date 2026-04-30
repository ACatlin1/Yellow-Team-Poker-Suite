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
import json
import importlib
from dataclasses import dataclass, field
from typing import Optional
from core.cards import Deck


class CustomStateEncoder(json.JSONEncoder):
    """Dynamically converts custom Python objects into dictionaries."""
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            d = obj.__dict__.copy()
            d["__class__"] = obj.__class__.__name__
            d["__module__"] = obj.__class__.__module__
            return d
        return super().default(obj)


def custom_state_decoder(d):
    """Dynamically rebuilds Python objects from the JSON dictionaries."""
    if "__class__" in d and "__module__" in d:
        try:
            module = importlib.import_module(d["__module__"])
            class_ = getattr(module, d["__class__"])
            
            # Recreate the object while bypassing the __init__ method
            obj = class_.__new__(class_)
            for key, value in d.items():
                if key not in ("__class__", "__module__"):
                    setattr(obj, key, value)
            return obj
        except Exception as e:
            print(f"Decode error: {e}")
    return d


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
    variant_name: str = "Texas Holdem"
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
    actions_this_round: int = 0
    winner: Optional[str] = None


    def to_json(self) -> str:
        """Converts the current state into a JSON string using the custom encoder."""
        return json.dumps(self, cls=CustomStateEncoder)


    @classmethod
    def from_json(cls, json_str: str):
        """Creates a GameState object from a received JSON string."""
        return json.loads(json_str, object_hook=custom_state_decoder)


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
