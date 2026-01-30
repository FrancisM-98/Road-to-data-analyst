import random
from typing import List, Optional

class Card:
    def __init__(self, value: int, card_type: str = "number"):
        self.value = value
        self.card_type = card_type  # "number", "modifier", "action"

    def __repr__(self):
        return f"[{self.value}]" if self.card_type == "number" else f"[{self.card_type.upper()}]"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.value == other.value and self.card_type == other.card_type
        return False

class Deck:
    def __init__(self):
        self.cards = []
        self._build_deck()

    def _build_deck(self):
        # Flip 7 Distribution logic
        # 0: 0 cards? (Actually 0 is usually not in Flip 7 unless custom?)
        # 1: 1 card
        # 2: 2 cards
        # ...
        # 12: 12 cards
        # Total number cards: 1+2+3+4+5+6+7+8+9+10+11+12 = 78 cards
        
        self.cards = []
        for i in range(1, 13):
            for _ in range(i):
                self.cards.append(Card(i))
        
        # TODO: Add special Action/Modifier cards later
        # For now, just focus on the number core loop
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        if not self.cards:
            return None
        return self.cards.pop()

    def shuffle(self):
        random.shuffle(self.cards)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.total_score = 0
        self.is_active = True
        self.second_life = False # New attribute

    def reset_round(self):
        self.hand = []
        self.is_active = True
        # second_life persists? Usually yes, until used. 
        # But for balance maybe resets? Let's keep it persistent for now as a "META" trade.

    def calculate_round_score(self) -> int:
        return sum(card.value for card in self.hand if card.card_type == "number")

    def has_duplicate(self, new_card: Card) -> bool:
        if new_card.card_type != "number":
            return False
            
        for card in self.hand:
            if card.value == new_card.value:
                return True
        return False

    def add_card(self, card: Card):
        self.hand.append(card)

    def remove_card_by_value(self, value: int) -> Optional[Card]:
        for i, card in enumerate(self.hand):
            if card.value == value:
                return self.hand.pop(i)
        return None

class Deal:
    def __init__(self, proposer: Player, target: Player):
        self.proposer = proposer
        self.target = target
        
        # Terms
        self.gives_cards: List[Card] = []
        self.receives_cards: List[Card] = []
        
        # Actions
        self.action_cancel_bust = False
        self.action_grant_second_life = False
        self.action_force_draw = 0 # Number of cards
        self.action_force_hit = False # Ban Stay
        self.action_discard_highest = False
        self.action_side_bet = False # Chicken Game
        
    def __repr__(self):
        desc = f"Deal between {self.proposer.name} & {self.target.name}:"
        if self.gives_cards: desc += f"\n  - Gives {self.gives_cards}"
        if self.receives_cards: desc += f"\n  - Gets {self.receives_cards}"
        if self.action_cancel_bust: desc += "\n  - [!] CANCEL BUST"
        if self.action_grant_second_life: desc += "\n  - [+] Grant Second Life"
        if self.action_force_draw > 0: desc += f"\n  - [!] Force Draw {self.action_force_draw}"
        if self.action_force_hit: desc += "\n  - [!] Force HIT (No Stay)"
        if self.action_discard_highest: desc += "\n  - [!] Discard Highest Card"
        if self.action_side_bet: desc += "\n  - [?] CHICKEN GAME BET"
        return desc
