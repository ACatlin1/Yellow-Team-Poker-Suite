"""
**************************************************************************

cards.py is for:

creating card objects
creating a deck of card objects

**************************************************************************
"""


import random


class Card:
    """ 
    Build Card objects
    Define constants for easy access and reuse
    Organize them for easy use in scoring
    """
    SUITS = ("Clubs", "Diamonds", "Hearts", "Spades")
    RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")
    
    # Map ranks to integers for easy comparison in the scoring engine
    RANK_VALUES = {rank: i + 2 for i, rank in enumerate(RANKS)}


    def __init__(self, suit: str, rank: str):
        if suit not in self.SUITS or rank not in self.RANKS:
            raise ValueError(f"Invalid card: {rank} of {suit}")
        
        self.suit = suit
        self.rank = rank
        self.value = self.RANK_VALUES[rank]
        self.is_face_up = False


    def __repr__(self):
        """Standardizes the output to be rank-suit"""
        return f"{self.rank} of {self.suit}"


    def __eq__(self, other):
        """Allows comparing two cards: card1 == card2"""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit


    def flip(self):
        """Toggle the visibility state."""
        self.is_face_up = not self.is_face_up


class Deck:
    """
    Build a group of 52 Card objects to function as a deck
    Allow the deck to be reset
    Allow the deck to be shuffled
    Draw 1 card from the deck
    Know how many cards are left in the deck to prevent going out of bounds
    """
    def __init__(self):
        self.cards = []
        self.reset()


    def reset(self):
        """Fill the deck with 52 new Card objects"""
        self.cards = [
            Card(suit, rank) 
            for suit in Card.SUITS 
            for rank in Card.RANKS
        ]


    def shuffle(self):
        """Use random to get a shuffle"""
        random.shuffle(self.cards)


    def draw(self, num=1):
        """Removes 'num' cards from the top of the deck and returns a list of Card objects"""
        if num > len(self.cards):
            raise ValueError("Not enough cards left in the deck!")
        
        drawn_cards = [self.cards.pop() for _ in range(num)]
        return drawn_cards


    def __len__(self):
        """Use len(deck) to see cards remaining"""
        return len(self.cards)