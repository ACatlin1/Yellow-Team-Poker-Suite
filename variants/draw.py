"""
**************************************************************************
draw.py is for:

the poker game type WITH card draw mechanics

**************************************************************************
"""


from core.players import Player


class Draw():
    def __init__(self, players, deck):
        self.players = players
        self.deck = deck

        self.small_blind = 10
        self.large_blind = 20
        self.variant_name = "5-Card Draw"

   
    def deal_initial_cards(self):
        """Deal 5 hole cards face down to every player"""
        for p in self.players:
            hole_card = self.deck.draw(5)
            p.hand.add_cards(hole_card)

    def discard_and_draw(self, player: Player, indices: list[int]):
        """
        Takes the indices of cards selected from the GUI.
        Removes those cards and deals fresh ones.
        """
        if len(indices) > 3:
            return False # Don't allow more than 3
            
        # Remove the cards (High to Low index)
        for index in sorted(indices, reverse=True):
            player.hand.cards.pop(index)
            
        # Draw the exact same number of new cards
        new_cards = self.deck.draw(len(indices))
        player.hand.add_cards(new_cards)
        