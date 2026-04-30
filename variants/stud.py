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

        self.small_blind = 10
        self.large_blind = 20
        self.variant_name = "7-Card Draw"


    def deal_initial_cards(self):
        for p in self.players:
            # 2 Face down cards
            down_cards = self.deck.draw(2)
            p.hand.add_cards(down_cards)
            # 1 Face up card (Door Card)
            door_card = self.deck.draw(1)
            door_card[0].is_face_up = True
            p.hand.add_cards(door_card)


    def deal_street_card(self, face_up=True):
        """Deals exactly one card to every active player during Streets 4-7."""
        for p in self.players:
            # Only deal cards to players who are still in the hand
            if not p.is_folded:
                card_list = self.deck.draw(1)
                card_list[0].is_face_up = face_up
                p.hand.add_cards(card_list)

        """Required by ABC, but logic is handled by UIManager."""
        pass