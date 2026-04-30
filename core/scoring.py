"""
**************************************************************************

scoring.py is for:

scoring resolution logic

**************************************************************************
"""


# Struct will help in scoring hands, ranked in order
scoring_ranks = {
    "High Card": 1,
    "Pair": 2,
    "Two Pair": 3,
    "Three of a kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10
}


from collections import Counter
from itertools import combinations

class Evaluator:
    @staticmethod
    def get_score(cards):
        """
        Makes a list of 5 Card objects
        It turns into a tupple of (Hand_Rank_Int, Tiebreaker_List)
        This gives scoring rank and high card for tie breaker
        """
        ranks = sorted([c.value for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        
        # Check for Flush and Straight
        is_flush = len(set(suits)) == 1
        is_straight = (max(ranks) - min(ranks) == 4) and len(set(ranks)) == 5
        is_royal = set(ranks) == {10, 11, 12, 13, 14}
        
        # 1. Royal FLush
        if is_flush and is_royal:
            return (10, ranks)
        
        # 2. Straight Flush
        if is_straight and is_flush:
            return (9, ranks)
        
        # 3. Four of a Kind
        if counts == [4, 1]:
            # Move the quad rank to the front of the tiebreaker
            quad_rank = [r for r in rank_counts if rank_counts[r] == 4]
            return (8, quad_rank + [r for r in ranks if r != quad_rank[0]])

        # 4. Full House
        if counts == [3, 2]:
            return (7, ranks)
        
        # 5. Flush
        if is_flush:
            return (6, ranks)

        # 6. Striaght
        if is_straight:
            return (5, ranks)

        # 7. Three of a Kind
        if counts == [3,1,1]:
            tri_rank = [t for t in rank_counts if rank_counts[t] == 3]
            return (4, tri_rank + [t for t in ranks if t != tri_rank[0]])

        # 8. Two Pair
        if counts == [2,2,1]:
            duo_rank = [d for d in rank_counts if rank_counts[d] == 2]
            return (2, duo_rank + [d for d in ranks if d != duo_rank[0]])

        # 9. Pair
        if counts == [2,1,1,1]:
            return (1, ranks)
        
        # 10. Default: High Card
        return (0, ranks)
    
# Determine the winner
def best_five(cards):
    best = None
    for combo in combinations(cards, 5):
        score = Evaluator.get_score(combo)
        if best == None or score > best:
            best = score
    return best
