"""
**************************************************************************

holdem.py is for:

the poker game type with community cards and river cards.

**************************************************************************
"""

class TexasHoldem():
    def __init__(self, players, deck, community_cards):
        self.players = players
        self.deck = deck
        self.community_cards = community_cards

        self.small_blind = 10
        self.large_blind = 20
        self.variant_name = "Texas Hold'em"

    def deal_initial_cards(self):
        for p in self.players:
            # Draw 2 cards from the deck
            cards = self.deck.draw(2)
            p.hand.add_cards(cards)

    def deal_community_cards(self, count: int):
        new_cards = self.deck.draw(count)
        for card in new_cards:
            card.is_face_up = True
        self.community_cards.extend(new_cards)

