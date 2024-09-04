import numpy as np
import json
from datetime import datetime
from combination_list import combinations  # Import the combinations
from wallet_manager import place_bet, add_winnings, get_player_balance
from jackpot_manager import increment_jackpot, check_jackpot_win, load_jackpot, reset_jackpot

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
        # Generate 15 symbols (3 rows x 5 columns)
        return [
            [np.random.choice(list(reels[f'Reel{i+1}'].keys()), p=reel_probabilities[f'Reel{i+1}'])
             for _ in range(3)]
            for i in range(5)
        ]

    def check_win(result):
        """Check if the spin result matches any winning combination across multiple paylines."""
        total_points = 0
        triggered_events = []
        winning_paylines = []
        
        # Define paylines (indices of symbols to check)
        paylines = [
            [(0,0), (1,0), (2,0), (3,0), (4,0)],  # Horizontal top
            [(0,1), (1,1), (2,1), (3,1), (4,1)],  # Horizontal middle
            [(0,2), (1,2), (2,2), (3,2), (4,2)],  # Horizontal bottom
            [(0,0), (1,1), (2,2), (3,1), (4,0)],  # V-shape
            [(0,2), (1,1), (2,0), (3,1), (4,2)],  # Inverted V-shape
            [(0,0), (1,2), (2,1), (3,2), (4,0)],  # W-shape
            [(0,2), (1,0), (2,1), (3,0), (4,2)]   # M-shape
        ]

        payline_names = [
            "Horizontal top", "Horizontal middle", "Horizontal bottom",
            "V-shape", "Inverted V-shape", "W-shape", "M-shape"
        ]

        for i, payline in enumerate(paylines):
            line_result = [result[x][y] for x, y in payline]
            
            for combo in combinations:
                matches = all(
                    symbol == combo['symbols'][i] or combo['symbols'][i] == '*'
                    for i, symbol in enumerate(line_result)
                )
                if matches:
                    total_points += combo['points']
                    winning_paylines.append(payline_names[i])
                    if 'trigger' in combo:
                        triggered_events.append(combo['trigger'])

        return total_points, triggered_events, winning_paylines

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
        current_jackpot = load_jackpot()
        print(f"Current balance: ${current_balance:.2f}")
        print(f"Current jackpot: ${current_jackpot:.2f}")
        
        if current_balance < bet_amount:
            print("Not enough balance to place bet.")
            return

        if place_bet(bet_amount):
            new_jackpot = increment_jackpot(bet_amount)
            print(f"Placing bet: ${bet_amount:.2f}")
            print(f"Jackpot increased to: ${new_jackpot:.2f}")
            print("Spinning the reels...")
            result = spin_reels()
            
            # Display result as a 3x5 grid
            for row in range(3):
                print(" | ".join(result[col][row] for col in range(5)))

            if check_jackpot_win(result):
                print(f"Congratulations! You've won the jackpot of ${new_jackpot:.2f}!")
                add_winnings(new_jackpot)
                reset_jackpot()
            else:
                points, events, winning_paylines = check_win(result)
                print(f'Points won: {points}')
                
                if winning_paylines:
                    print(f"Payline hit: {winning_paylines[0]}")
                    if len(winning_paylines) > 1:
                        print("Additional winning paylines:")
                        for payline in winning_paylines[1:]:
                            print(f"- {payline}")
                else:
                    print("No paylines hit")

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