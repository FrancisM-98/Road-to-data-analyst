from game import Flip7Game

def main():
    print("Welcome to FLIP 7: Negotiation Edition")
    game = Flip7Game()
    
    # Setup
    while True:
        name = input("Enter player name (or empty to start): ").strip()
        if not name:
            if len(game.players) < 2:
                print("Need at least 2 players!")
                continue
            break
        game.add_player(name)
        
    print(f"\nGame starting with {len(game.players)} players.")
    
    round_num = 1
    while True:
        print(f"\n=== ROUND {round_num} ===")
        game.start_round()
        
        # Round Loop
        while True:
            # Check if all players out/banked
            active_count = len([p for p in game.players if p.is_active])
            if active_count == 0:
                break
                
            for player in game.players:
                if player.is_active:
                    game.play_turn(player)
                    # Check instant win conditions
                    if any(p.total_score >= game.winning_score for p in game.players):
                         break
            
            # Double check loop break
            if any(p.total_score >= game.winning_score for p in game.players):
                 break
        
        # End of Round Scoring
        print("\n=== ROUND OVER ===")
        for p in game.players:
            # Add round points to total
            round_pts = p.calculate_round_score()
            # If they busted (hand empty), score is 0
            if len(p.hand) == 0: round_pts = 0
            
            p.total_score += round_pts
            print(f"{p.name}: +{round_pts} pts => Total: {p.total_score}")
            
        # Win Check
        winner = next((p for p in game.players if p.total_score >= game.winning_score), None)
        if winner:
            print(f"\n\nWINNER IS {winner.name} with {winner.total_score} points!")
            break
            
        round_num += 1
        input("Press Enter to start next round...")

if __name__ == "__main__":
    main()
