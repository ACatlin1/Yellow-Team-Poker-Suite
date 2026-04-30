"""
**************************************************************************

npc.py is for:

creating virtual opponents for local play

**************************************************************************
"""


from core.scoring import Evaluator
from core.scoring import best_five
from itertools import combinations


class BotAI:
    def choose_action(self, player, game_state):
        """
        Returns a dict like:
        {"player_name": player.name, "action": "bet"/"fold"/"call", "amount": X}
        """

        # If pre-flop: use a super simple rule based on hole cards
        if game_state.phase == "pre-flop":
            return self.preflop_logic(player, game_state)
        
        # Let the bot recognize draw-phase
        elif game_state.phase == "draw":
            # Bot keeps all cards for now (implement better logic later)
            return {"player_name": player.name, "action": "discard", "indices": []}

        # Post-flop and later: use hand strength
        return self.postflop_logic(player, game_state)

    def preflop_logic(self, player, game_state):
        cards = player.hand.cards
        
        # Differentiate between appropriate starting hands for game types
        # Draw uses 5 initial cards
        if len(cards) >= 5:
            return self.postflop_logic(player, game_state)
        
        # Safety fallback if cards are missing
        if len(cards) < 2:
            return {"player_name": player.name, "action": "bet", "amount": 0}
        
        # Hold Em deals 2 cards. Stud deals 3, but the bot can work fine with the first 2
        c1 = cards[0]
        c2 = cards[1]

        high_ranks = {11, 12, 13, 14}  # Let the bot see J, Q, K, A

        # Pocket pair or both high cards - raise
        if c1.value == c2.value or (c1.value in high_ranks and c2.value in high_ranks):
            amount = min(50, player.chips)
            return {"player_name": player.name, "action": "bet", "amount": amount} # bet 50

        # One high card - call/check
        if c1.value in high_ranks or c2.value in high_ranks:
            return {"player_name": player.name, "action": "bet", "amount": 10} # bet 10

        # Nothing - fold if there's a bet to match, otherwise check
        if game_state.current_bet_to_match > player.current_bet:
            return {"player_name": player.name, "action": "fold", "amount": 0} # fold
        else:
            return {"player_name": player.name, "action": "bet", "amount": 0}  # check

    def postflop_logic(self, player, game_state):
        # Evaluate best 5-card hand from hole + community
        all_cards = player.hand.cards + game_state.community_cards
        to_call = game_state.current_bet_to_match - player.current_bet

        if len(all_cards) < 5:
            # Just call/check small bets until we have 5 cards to evaluate
            if to_call <= 20:
                amount = max(to_call, 0)
                return {"player_name": player.name, "action": "bet", "amount": amount}
            else:
                return {"player_name": player.name, "action": "fold", "amount": 0}
        best_score = best_five(all_cards)

        rank_value, tiebreakers = best_score

        # Generic action thresholds
        if rank_value >= 5:
            # Strong hand - raise
            amount = min(to_call + 50, player.chips)
            return {"player_name": player.name, "action": "bet", "amount": amount}

        if rank_value >= 3:
            # Medium hand - call if not too expensive
            if to_call <= player.chips * 0.3:
                amount = max(to_call, 10)
                return {"player_name": player.name, "action": "bet", "amount": amount}
            else:
                return {"player_name": player.name, "action": "fold", "amount": 0}

        if rank_value == 2:
            # Weak pair - call small, fold big
            if to_call <= 10:
                return {"player_name": player.name, "action": "bet", "amount": to_call}
            else:
                return {"player_name": player.name, "action": "fold", "amount": 0}

        # High card only
        if to_call == 0:
            # Check
            return {"player_name": player.name, "action": "bet", "amount": 0}
        else:
            # Fold to pressure
            return {"player_name": player.name, "action": "fold", "amount": 0}
