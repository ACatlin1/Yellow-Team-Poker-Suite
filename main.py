from core.cards import Deck
from core.players import Player
from ui.manager import UIManager

UIManager()

# WIP test1
deck = Deck()
deck.shuffle()

p1 = Player("User")
p2 = Player("CPU 1", is_cpu=True)

# Deal 2 cards to each (Hold'em style)
p1.hand.add_cards(deck.draw(2))
p2.hand.add_cards(deck.draw(2))

print(p1)
