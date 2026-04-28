"""
**************************************************************************
stud.py is for:

the poker game type WITHOUT card drawing mechanics

**************************************************************************
"""


class Stud():
    def __init__(self, players, deck):
        self.players = players
        self.deck = deck

    def deal_cards(self):
        """Standard Stud deal: 2 cards down, 1 face up to each player."""
        self.deal_initial_cards()

    def deal_initial_cards(self):
        for p in self.players:
            # 2 Face down cards
            down_cards = self.deck.draw(2)
            p.hand.add_cards(down_cards)
            # 1 Face up card (Door Card)
            door_card = self.deck.draw(1)
            door_card[0].is_face_up = True
            p.hand.add_cards(door_card)

    def small_blind(self):
        return 5

    def large_blind(self):
        return 10

    def determine_winner(self):
        """This will be triggered by logic.handle_showdown."""
        pass 

    def play_round(self):
        """Required by ABC, but logic is handled by UIManager."""
        pass