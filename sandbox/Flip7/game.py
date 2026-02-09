from models import Deck, Player, Card, Deal
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
                if not player.has_duplicate(card):
                    print(f"  Current Hand: {player.hand + [card]}") # Preview hand including new card
                
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

    def suggest_trade_logic(self, active_player: Player, target_player: Player, busting_card: Optional[Card] = None) -> List[Deal]:
        deals = []
        
        # 1. The Bailout (If Busting)
        if busting_card:
            deal = Deal(active_player, target_player)
            deal.action_cancel_bust = True
            deal.action_force_draw = 2 # Cost: Draw 2 more
            deal.gives_cards = [busting_card] # Logic: you take this
            deals.append(deal)
            
            # 2. Scrapyard (Self sacrifice)
            deal2 = Deal(active_player, target_player) # Target doesn't matter much here but needed for structure
            deal2.action_discard_highest = True
            deal2.action_cancel_bust = True
            deals.append(deal2)

        # 3. The Forced March (Aggressive)
        if not busting_card:
            deal = Deal(active_player, target_player)
            deal.action_force_hit = True
            # Cost? Maybe give a good card?
            if active_player.hand:
                deal.gives_cards = [active_player.hand[0]] # Just first one for demo
            deals.append(deal)

        return deals

    def execute_deal(self, deal: Deal):
        print(f"\nExecuting Deal: {deal}")
        
        # Transfer Cards
        for c in deal.gives_cards:
            if c in deal.proposer.hand:
                deal.proposer.hand.remove(c)
                deal.target.add_card(c)
                print(f"  -> Transferred {c} from {deal.proposer.name} to {deal.target.name}")
        
        for c in deal.receives_cards:
            if c in deal.target.hand:
                deal.target.hand.remove(c)
                deal.proposer.add_card(c)
                print(f"  -> Transferred {c} from {deal.target.name} to {deal.proposer.name}")

        # Meta Actions
        if deal.action_grant_second_life:
            deal.target.second_life = True
            print(f"  -> {deal.target.name} granted SECOND LIFE!")
            
        if deal.action_discard_highest:
            # Find max card
            nums = [c for c in deal.proposer.hand if c.card_type == 'number']
            if nums:
                max_card = max(nums, key=lambda x: x.value)
                deal.proposer.hand.remove(max_card)
                print(f"  -> {deal.proposer.name} sacrificed {max_card} to the Scrap Yard!")

        if deal.action_force_hit:
            print(f"  -> {deal.target.name} is FORCED TO HIT next turn!")
            # Logic needs to be handled in play_turn loop via a flag on player?
            # For prototype, we just print it. Real impl needs state.

        if deal.action_force_draw > 0:
            print(f"  -> {deal.proposer.name} must draw {deal.action_force_draw} extra cards!")
            for _ in range(deal.action_force_draw):
                c = self.deck.draw()
                if c:
                    print(f"    Forced Draw: {c}")
                    if deal.proposer.has_duplicate(c):
                        print("    ...and they BUSTED on the forced draw!")
                        return False # Failed execution essentially, or just bust logic takes over
                    deal.proposer.add_card(c)

        if deal.action_cancel_bust:
            print("  -> Bust Cancelled! Player stays alive.")
            return True # Signal success

        return True

    def initiate_negotiation(self, active_player: Player):
        print("\n--- NEGOTIATION TABLE ---")
        targets = [p for p in self.players if p != active_player]
        if not targets: return

        for i, p in enumerate(targets):
            print(f"{i+1}. {p.name} (Hand: {p.hand})")
        
        try:
            choice = int(input("Select partner (number) or 0: "))
            if choice == 0: return
            target = targets[choice-1]
        except: return

        # ADVISOR
        print("\n[A]dvisor Suggestions:")
        deals = self.suggest_trade_logic(active_player, target)
        for i, d in enumerate(deals):
            print(f"{i+1}. {d}")
        
        print(f"{len(deals)+1}. Custom Trade (Not impl yet)")
        
        try:
            d_choice = int(input("Choose deal to offer: "))
            if 1 <= d_choice <= len(deals):
                offer = deals[d_choice-1]
                # Ask Target
                agree = input(f"{target.name}, do you accept? [y/n] ")
                if agree.lower() == 'y':
                    self.execute_deal(offer)
        except: pass

    def resolve_bust_negotiation(self, player: Player, busting_card: Card) -> bool:
        print(f"\n!!! SOS: BUSTING with {busting_card} !!!")
        
        # Auto-call advisor for ALL targets
        possible_deals = []
        for p in self.players:
            if p == player or not p.is_active: continue
            possible_deals.extend(self.suggest_trade_logic(player, p, busting_card))
            
        if not possible_deals:
            print("Advisor has no ideas. You are doomed.")
            return False
            
        for i, d in enumerate(possible_deals):
            print(f"{i+1}. {d}")
            
        try:
            sel = int(input("Select SOS Deal (0 to die): "))
            if sel == 0: return False
            chosen_deal = possible_deals[sel-1]
            
            # Ask Target (unless self-sacrifice)
            if chosen_deal.action_discard_highest:
                # Self action, no approval needed? or maybe purely desperate
                return self.execute_deal(chosen_deal)
            else:
                agree = input(f"{chosen_deal.target.name}, save {player.name}? [y/n] ")
                if agree.lower() == 'y':
                    return self.execute_deal(chosen_deal)
        except: pass
        
        return False

