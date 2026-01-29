from models import Deck, Player, Card
from typing import List, Optional

class Flip7Game:
    def __init__(self):
        self.players: List[Player] = []
        self.deck = Deck()
        self.current_player_idx = 0
        self.winning_score = 200

    def add_player(self, name: str):
        self.players.append(Player(name))

    def start_round(self):
        self.deck = Deck() # Fresh deck
        for p in self.players:
            p.reset_round()
            # Deal initial card? Usually 1 card face up
            initial = self.deck.draw()
            if initial:
                p.add_card(initial)
        
        print("\n--- NEW ROUND START ---")
        self._print_status()

    def _print_status(self):
        for p in self.players:
            status = "ACTIVE" if p.is_active else "BANKED/OUT"
            print(f"{p.name}: {p.hand} (Score: {p.calculate_round_score()}) [{status}]")

    def play_turn(self, player: Player):
        if not player.is_active:
            return

        print(f"\n> It is {player.name}'s turn.")
        print(f"  Hand: {player.hand}")
        
        while True:
            action = input(f"{player.name}, [H]it, [S]tay, or [N]egotiate? ").lower().strip()
            
            if action == 'n':
                self.initiate_negotiation(player)
                # After negotiation, player MIGHT turn end or continue?
                # User said "It can happen anytime", implying it doesn't consume the turn?
                # For now let's assume it circles back to choice
                continue

            if action == 's':
                player.is_active = False # Banked
                print(f"{player.name} chooses to Stay. Banked {player.calculate_round_score()} points.")
                return

            if action == 'h':
                card = self.deck.draw()
                if not card:
                    print("Deck empty!")
                    return
                
                print(f"  Drew: {card}")
                
                # Check Bust
                if player.has_duplicate(card):
                    print(f"  !!! OH NO! Duplicate {card.value} !!!")
                    success = self.resolve_bust_negotiation(player, card)
                    if not success:
                        print(f"  BUST! {player.name} is out for this round.")
                        player.hand = [] # Lose points
                        player.is_active = False
                    else:
                        print(f"  Negotiation saved you! Drawing replacement...")
                        # In the new rule, if saved, they "pull another card instead"
                        # Recursive call or just simple redraw? Let's do simple redraw loop here
                        continue
                else:
                    player.add_card(card)
                    
                    # Check Flip 7
                    unique_count = len([c for c in player.hand if c.card_type == "number"]) 
                    # Note: Need more robust unique check if duplicates allowed by trades
                    # Actually standard rules say 7 unique values = Flip 7
                    
                    if unique_count >= 7:
                        # Bonus!
                        print(f"*** FLIP 7! {player.name} wins the round! ***")
                        player.total_score += 15
                        # End round for everyone effectively
                        for p in self.players: p.is_active = False
                        return
                    
                    continue # Player keeps going? Or turn passes? 
                    # Standard Flip 7 is push-your-luck: keep going until you stop or bust
                    # So continue loop.
            
            print("Invalid command.")

    def initiate_negotiation(self, active_player: Player):
        print("\n--- NEGOTIATION TABLE ---")
        # List other players
        targets = [p for p in self.players if p != active_player]
        if not targets:
            print("No one to trade with!")
            return

        for i, p in enumerate(targets):
            print(f"{i+1}. {p.name} (Hand: {p.hand})")
        
        try:
            choice = int(input("Select partner (number) or 0 to cancel: "))
            if choice == 0: return
            target = targets[choice-1]
        except:
            return

        print(f"Talking to {target.name}...")
        # Very simple trade logic for v1
        # "Give card X to target"
        try:
            val_to_give = int(input(f"Value of card to GIVE to {target.name} (0 for none): "))
            
            # Verify possession
            card_to_give = None
            if val_to_give > 0:
                card_to_give = active_player.remove_card_by_value(val_to_give)
                if not card_to_give:
                    print("You don't have that card.")
                    return

            if card_to_give:
                target.add_card(card_to_give)
                print(f"Deal done! Gave {card_to_give} to {target.name}.")
            else:
                print("Negotiation cancelled.")
        except ValueError:
            print("Invalid input")


    def resolve_bust_negotiation(self, player: Player, busting_card: Card) -> bool:
        """
        Returns True if player was saved (gave card away), False if they Bust.
        """
        print(f"\n!!! SOS NEGOTIATION !!!")
        print(f"You drew a {busting_card}. You already have one.")
        print("Does anyone want this card? (Negotiate!)")
        
        # Ask other players if they want it
        start_idx = self.players.index(player)
        # Iterate through others
        others = self.players[start_idx+1:] + self.players[:start_idx]
        
        for p in others:
            if not p.is_active: continue
            
            # Check if they can even take it (don't want to bust them usually, but maybe they want it?)
            if p.has_duplicate(busting_card):
                print(f"{p.name} surely doesn't want it (has {busting_card.value}).")
                continue
                
            choice = input(f"{p.name}, do you want the {busting_card.value} from {player.name}? [y/n] ")
            if choice.lower() == 'y':
                p.add_card(busting_card)
                print(f"{p.name} accepted the card! {player.name} is SAFE.")
                return True
        
        print("No takers. :(")
        return False
