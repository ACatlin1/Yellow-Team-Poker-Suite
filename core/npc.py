"""
**************************************************************************

npc.py is for:

creating virtual opponents for local play

**************************************************************************
"""


from scoring import Evaluator
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

        # Post-flop and later: use hand strength
        return self.postflop_logic(player, game_state)

    def preflop_logic(self, player, game_state):
        c1, c2 = player.hand.cards
        high_ranks = {11, 12, 13, 14}  # J, Q, K, A

        # Pocket pair or both high cards → raise
        if c1.value == c2.value or (c1.value in high_ranks and c2.value in high_ranks):
            amount = min(50, player.chips)
            return {"player_name": player.name, "action": "bet", "amount": amount}

        # One high card → call/check
        if c1.value in high_ranks or c2.value in high_ranks:
            return {"player_name": player.name, "action": "bet", "amount": 10}

        # Trash → fold if there's a bet to match, otherwise check
        if game_state.current_bet_to_match > player.current_bet:
            return {"player_name": player.name, "action": "fold", "amount": 0}
        else:
            return {"player_name": player.name, "action": "bet", "amount": 0}  # check

    def postflop_logic(self, player, game_state):
        # Evaluate best 5-card hand from hole + community
        all_cards = player.hand.cards + game_state.community_cards
        best_score = self.best_five(all_cards)

        rank_value, tiebreakers = best_score

        # Very rough thresholds:
        # 5+ (Straight or better) → aggressive
        # 3–4 (Two pair / trips) → moderate
        # 2 (Pair) → cautious
        # 1 (High card) → mostly fold

        to_call = game_state.current_bet_to_match - player.current_bet

        if rank_value >= 5:
            # Strong hand → raise
            amount = min(to_call + 50, player.chips)
            return {"player_name": player.name, "action": "bet", "amount": amount}

        if rank_value >= 3:
            # Medium hand → call if not too expensive
            if to_call <= player.chips * 0.3:
                amount = max(to_call, 10)
                return {"player_name": player.name, "action": "bet", "amount": amount}
            else:
                return {"player_name": player.name, "action": "fold", "amount": 0}

        if rank_value == 2:
            # Weak pair → call small, fold big
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

    def best_five(self, cards):
        best = (0, [])
        for combo in combinations(cards, 5):
            score = Evaluator.get_score(combo)
            if score > best:
                best = score
        return best