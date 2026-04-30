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

    def deal_cards(self):
        """Implementation of abstract method for initial deal."""
        self.deal_initial_cards()

   
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
        
        return True

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