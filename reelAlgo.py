import numpy as np
import combination_list as cl
from combination_list import combinations  # Import the combinations
from wallet_manager import place_bet, add_winnings, get_player_balance

# 1. Define game elememnts
# SYMBOLS LIST
sym = ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN']

def selected_model():

    # Reels configuration: Defining probabilities for each symbol on each reel
    reels = {
        'Reel1':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 1
        'Reel2':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 2
        'Reel3':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 3
        'Reel4':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 4
        'Reel5':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 5
    }
    
    # Step 2: Develop Initial spin_reels() Function
    def spin_reels():
        """Simulates spinning of the reels using weighted random selection with numpy."""
        # Pre-calculate probabilities for each reel
        reel_probabilities = {
            reel_name: np.array(list(reel.values())) / sum(reel.values())
            for reel_name, reel in reels.items()
        }
        # Use list comprehension for more concise code
        return [
            np.random.choice(list(reel.keys()), p=reel_probabilities[reel_name])
            for reel_name, reel in reels.items()
        ]
    
    def check_win(result):
        """Check if the spin result matches any winning combination."""
        total_points = 0
        triggered_events = []

        for combo in combinations:
            matches = all(
                symbol == combo['symbols'][i] or combo['symbols'][i] == '*'
                for i, symbol in enumerate(result)
            )
            if matches:
                total_points += combo['points']
                if 'trigger' in combo:
                    triggered_events.append(combo['trigger'])

        return total_points, triggered_events

    def play_game(bet_amount=10):
        current_balance = get_player_balance()
        print(f"Current balance: ${current_balance:.2f}")
        
        if current_balance < bet_amount:
            print("Not enough balance to place bet.")
            return

        if place_bet(bet_amount):
            print(f"Placing bet: ${bet_amount:.2f}")
            print("Spinning the reels...")
            result = spin_reels()
            print(f'Result: {" | ".join(result)}')

            points, events = check_win(result)
            print(f'Points won: {points}')
            if events:
                print(f'Triggered events: {", ".join(events)}')

            winnings = points * 0.1  # Convert points to actual winnings
            add_winnings(winnings)
            print(f"Winnings: ${winnings:.2f}")
            print(f"New balance: ${get_player_balance():.2f}")
        else:
            print("Error placing bet. Please try again.")

    # Example usage
    play_game()

selected_model()