import numpy as np
import json
from datetime import datetime
from combination_list import combinations  # Import the combinations
from wallet_manager import place_bet, add_winnings, get_player_balance

# 1. Define game elements
# SYMBOLS LIST
sym = ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']

def selected_model():
    # Reels configuration: Defining probabilities for each symbol on each reel
    reels = {
        'Reel1': {s: 1 for s in sym},  # Equal probability for simplicity
        'Reel2': {s: 1 for s in sym},
        'Reel3': {s: 1 for s in sym},
        'Reel4': {s: 1 for s in sym},
        'Reel5': {s: 1 for s in sym},
    }
    
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
    876u
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

    def log_result(result, bet_amount, points, winnings, balance):
        """Log the game result to a JSON file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "bet_amount": bet_amount,
            "points_won": points,
            "winnings": winnings,
            "balance_after": balance
        }

        try:
            with open('logs.json', 'r+') as f:
                data = json.load(f)
                data.append(log_entry)
                f.seek(0)
                json.dump(data, f, indent=4)
        except FileNotFoundError:
            with open('logs.json', 'w') as f:
                json.dump([log_entry], f, indent=4)

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
            new_balance = get_player_balance()
            print(f"Winnings: ${winnings:.2f}")
            print(f"New balance: ${new_balance:.2f}")

            # Log the result
            log_result(result, bet_amount, points, winnings, new_balance)
        else:
            print("Error placing bet. Please try again.")

    # Example usage
    play_game()

selected_model()