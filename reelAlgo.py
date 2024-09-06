import numpy as np
import json
from datetime import datetime
from functools import lru_cache
from combination_list import combinations
from wallet_manager import place_bet, add_winnings, get_player_balance, convert_to_tokens, convert_to_money, deposit_to_player, withdraw_to_bank
from jackpot_manager import increment_jackpot, check_jackpot_win, load_jackpot, reset_jackpot
from config_manager import get_reel_probabilities, get_symbol_payouts
from advanced_rng import SlotMachineRNG

# SYMBOLS LIST
sym = ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']

HOUSE_EDGE = 0.05  # 5% house edge

def selected_model():
    # Load reel configuration and symbol payouts from config_manager
    reels = get_reel_probabilities()
    symbol_payouts = get_symbol_payouts()
    
    # Define special symbols and trigger conditions
    BONUS_SYMBOL = "BONUS"
    BONUS_TRIGGER = 3  # Number of bonus symbols needed to trigger the bonus game

    # Create an instance of SlotMachineRNG
    rng = SlotMachineRNG()

    def spin_reels():
        """
        Generate a spin result using the advanced RNG.
        """
        return rng.generate_spin(reels)

    def check_bonus_trigger(symbols):
        """Check if the bonus round is triggered based on the number of BONUS symbols."""
        bonus_count = sum(symbol == BONUS_SYMBOL for reel in symbols for symbol in reel)
        print(f"Debug: BONUS symbols count: {bonus_count}")
        return bonus_count >= BONUS_TRIGGER

    def play_bonus_game():
        """Simulates a more balanced pick-a-box bonus game."""
        print("Bonus Round Triggered!")
        
        # Define prizes with their probabilities
        prizes = [
            (0, 30),     # 30% chance of winning nothing
            (10, 25),    # 25% chance of winning 10
            (20, 20),    # 20% chance of winning 20
            (50, 15),    # 15% chance of winning 50
            (100, 7),    # 7% chance of winning 100
            (200, 2),    # 2% chance of winning 200
            (500, 1)     # 1% chance of winning 500
        ]
        
        # Calculate the total weight
        total_weight = sum(weight for _, weight in prizes)
        
        # Generate a random number
        r = random.randint(1, total_weight)
        
        # Select the prize based on the random number
        current_weight = 0
        for prize, weight in prizes:
            current_weight += weight
            if r <= current_weight:
                if prize == 0:
                    print("Sorry, no bonus win this time!")
                else:
                    print(f"Congratulations! You won a bonus of ${prize}!")
                return prize

        # This should never happen, but just in case
        print("An error occurred in the bonus game.")
        return 0

    @lru_cache(maxsize=None)
    def calculate_symbol_probability(symbol, reel_index):
        reel = reels[f'Reel{reel_index + 1}']
        total = sum(reel.values())
        return reel.get(symbol, 0) / total

    def calculate_combination_probability(symbols):
        probabilities = [calculate_symbol_probability(symbol, i) if symbol != '*' else 1 
                         for i, symbol in enumerate(symbols)]
        return np.prod(probabilities)

    def check_win(result):
        total_points = 0
        max_payout = 0
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

        # Iterate through each payline
        for i, payline in enumerate(paylines):
            # Extract the symbols for the current payline
            line_result = [result[x][y] for x, y in payline]
            
            # Check each winning combination against the current payline
            for combo in combinations:
                matches = all(symbol == combo['symbols'][i] or combo['symbols'][i] == '*'
                              for i, symbol in enumerate(line_result))
                if matches:
                    total_points += combo['points']
                    max_payout = max(max_payout, symbol_payouts.get(combo['symbols'][0], 0))
                    winning_paylines.append(payline_names[i])
                    if 'trigger' in combo:
                        triggered_events.append(combo['trigger'])
                    break  # Stop checking after first match on this payline

        # Return the total points won, max payout, any triggered events, and the winning paylines
        return total_points, max_payout, triggered_events, winning_paylines

    def log_result(result, bet_amount, points, winnings, balance, jackpot_win=0, bonus_win=0, current_jackpot=0):
        """Log the game result to a JSON file, including jackpot and bonus information."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "bet_amount": bet_amount,
            "points_won": points,
            "regular_winnings": winnings - jackpot_win - bonus_win - (bet_amount if winnings > 0 else 0),
            "jackpot_win": jackpot_win,
            "bonus_win": bonus_win,
            "total_winnings": winnings,
            "balance_after": balance,
            "current_jackpot": current_jackpot
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

    def display_wallet():
        balance = get_player_balance()
        tokens = get_player_balance(get_tokens=True)
        print(f"Current balance: ${balance:.2f}")
        print(f"Current tokens: {tokens}")

    def exchange_menu():
        while True:
            display_wallet()
            print("\nExchange Menu:")
            print("1. Deposit Money")
            print("2. Convert Money to Tokens")
            print("3. Convert Tokens to Money")
            print("4. Withdraw Money to Bank")
            print("5. Return to Main Menu")
            choice = input("Enter your choice: ")

            if choice == '1':
                amount = float(input("Enter amount to deposit: $"))
                deposit_to_player(amount)
            elif choice == '2':
                amount = float(input("Enter amount to convert to tokens: $"))
                convert_to_tokens(amount, 10)  # Using an exchange rate of 1:10
            elif choice == '3':
                tokens = int(input("Enter number of tokens to convert: "))
                convert_to_money(tokens, 10)  # Using an exchange rate of 1:10
            elif choice == '4':
                amount = float(input("Enter amount to withdraw: $"))
                withdraw_to_bank(amount)
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def play_game(bet_amount=10, use_tokens=False):
        current_balance = get_player_balance(get_tokens=use_tokens)
        current_jackpot = load_jackpot()
        print(f"Current {'tokens' if use_tokens else 'balance'}: {'$' if not use_tokens else ''}{current_balance:.2f}")
        print(f"Current jackpot: ${current_jackpot:.2f}")
        
        if current_balance < bet_amount:
            print("Not enough balance to place bet.")
            return

        if place_bet(bet_amount, use_tokens):
            new_jackpot = increment_jackpot(bet_amount)
            print(f"Placing bet: {'$' if not use_tokens else ''}{bet_amount:.2f}")
            print(f"Jackpot increased to: ${new_jackpot:.2f}")
            print("Spinning the reels...")
            result = spin_reels()
            
            # Display result as a 3x5 grid
            for row in range(3):
                print(" | ".join(result[col][row] for col in range(5)))

            points, payout, events, winning_paylines = check_win(result)
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

            winnings = payout  # payout is now the actual amount, not a multiplier

            # Bonus points section
            print("Bonus points:")
            if check_bonus_trigger(result):
                print("Bonus round triggered!")
                bonus_win = play_bonus_game()
                if bonus_win > 0:
                    winnings += bonus_win
                    print(f"You won {'$' if not use_tokens else ''}{bonus_win:.2f} in the Bonus Round!")
                else:
                    print("No additional winnings from the Bonus Round.")
            else:
                print("No bonus round triggered.")

            if winnings > 0:
                winnings += bet_amount  # Add the original bet back if there's a win
                # Apply house edge
                winnings *= (1 - HOUSE_EDGE)
                print(f"Returning your original bet of {'$' if not use_tokens else ''}{bet_amount:.2f}")
                print(f"House edge of {HOUSE_EDGE*100}% applied")

            add_winnings(winnings, use_tokens)
            
            new_balance = get_player_balance(get_tokens=use_tokens)
            print(f"Total winnings: {'$' if not use_tokens else ''}{winnings:.2f}")
            print(f"New {'tokens' if use_tokens else 'balance'}: {'$' if not use_tokens else ''}{new_balance:.2f}")

            # Log the result
            log_result(result, bet_amount, points, winnings, new_balance, jackpot_win=0, bonus_win=0, current_jackpot=current_jackpot)
        else:
            print("Error placing bet. Please try again.")

    def main_menu():
        while True:
            print("\nMain Menu:")
            print("1. Play Game (Money)")
            print("2. Play Game (Tokens)")
            print("3. Exchange Currency")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                bet = float(input("Enter bet amount: $"))
                play_game(bet, use_tokens=False)
            elif choice == '2':
                bet = int(input("Enter bet amount (in tokens): "))
                play_game(bet, use_tokens=True)
            elif choice == '3':
                exchange_menu()
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    # Start the game
    main_menu()

# Run the game
selected_model()