"""
**************************************************************************

players.py is for:

player class
hand class

**************************************************************************
"""


from typing import List
from core.cards import Card


class Hand:
    """The cards held by a player."""
    def __init__(self):
        self.cards: List[Card] = []

    def add_cards(self, cards: List[Card]):
        # Gets a list of Card objects from the Deck
        self.cards.extend(cards)

    def discard(self, indices: List[int]):
        # Removes cards by index (specifically for 5-Card Draw)
        # Sort indices in reverse to avoid index shifting to pop cards
        for index in sorted(indices, reverse=True):
            self.cards.pop(index)

    def clear(self):
        # Resets hand for a new round
        self.cards = []

    def __repr__(self):
        return ", ".join([str(c) for c in self.cards]) if self.cards else "Empty Hand"


class Player:
    """
    This container holds all the things the player needs to manage
    """
    def __init__(self, name: str, initial_chips: int = 1000, is_cpu: bool = False):
        self.name = name
        self.hand = Hand()
        self.chips = initial_chips
        self.is_cpu = is_cpu
        
        # Track the state for the current round
        self.current_bet = 0
        self.is_folded = False
        self.is_all_in = False

    def bet(self, amount: int) -> int:
        # Removes chips from stack and returns the amount bet
        if amount >= self.chips:
            actual_bet = self.chips
            self.chips = 0
            self.is_all_in = True
        else:
            actual_bet = amount
            self.chips -= amount
        
        self.current_bet += actual_bet
        return actual_bet

    def reset_round_state(self):
        # Reset for every new deal
        self.hand.clear()
        self.current_bet = 0
        self.is_folded = False
        self.is_all_in = False

    def __repr__(self):
        return f"{self.name} (${self.chips}) - {'Folded' if self.is_folded else self.hand}"