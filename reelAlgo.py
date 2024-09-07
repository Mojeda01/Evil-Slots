import numpy as np
import json
from datetime import datetime
from functools import lru_cache
from combination_list import combinations
from wallet_manager import place_bet, add_winnings, get_player_balance, deposit_to_player, withdraw_to_bank
from jackpot_manager import increment_jackpot, check_jackpot_win, load_jackpot, reset_jackpot
from config_manager import get_reel_probabilities, get_symbol_payouts
from advanced_rng import SlotMachineRNG
from data_access import (
    create_player, get_player, update_player_balance,
    create_game_session, end_game_session, record_game_result,
    record_transaction, authenticate_player, get_token_conversion_rate, update_token_conversion_rate
)
from database import SessionLocal
import os
from dotenv import load_dotenv

# SYMBOLS LIST
sym = ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']

HOUSE_EDGE = 0.05  # 5% house edge

# Load environment variables
load_dotenv()

# Get user credentials from .env file
DB_USERNAME = os.getenv("DB_USERNAME", "marcoojeda")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # Empty string if no password is set

print("Script started")  # Debug print

def create_user_if_not_exists(username):
    db = SessionLocal()
    try:
        player = get_player(db, username)
        if not player:
            print(f"Creating new user: {username}")
            player = create_player(db, username, f"{username}@example.com", "", initial_balance=1000)
            print(f"User {username} created successfully")
        return player
    finally:
        db.close()

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

    return spin_reels, check_win, play_bonus_game  # Return any functions needed for the main game loop

# Database-related functions
def start_game():
    print(f"Attempting to start game for user: {DB_USERNAME}")  # Debug print
    player = create_user_if_not_exists(DB_USERNAME)
    if not player:
        print(f"Failed to create or retrieve user {DB_USERNAME}")
        return None, None
    
    db = SessionLocal()
    try:
        session = create_game_session(db, player.id, player.balance)
        print(f"Game session created for {player.username}")  # Debug print
        return player, session
    finally:
        db.close()

def update_balance(player_id, amount):
    db = SessionLocal()
    try:
        updated_player = update_player_balance(db, player_id, amount)
        return updated_player
    finally:
        db.close()

def end_game(session_id, final_balance):
    db = SessionLocal()
    try:
        ended_session = end_game_session(db, session_id, final_balance)
        return ended_session
    finally:
        db.close()

def record_spin(session_id, spin_number, bet_amount, outcome, winnings):
    db = SessionLocal()
    try:
        result = record_game_result(db, session_id, spin_number, bet_amount, outcome, winnings)
        return result
    finally:
        db.close()

def display_wallet(player):
    print(f"Current balance: ${player.balance:.2f}")
    # Remove the tokens display if it's not part of your Player model

def exchange_menu(player):
    virtual_wallet = 10000  # Start with a large amount in the virtual wallet
    while True:
        player.balance = get_player_balance(player)  # Update player balance from database
        conversion_rate = get_token_conversion_rate(SessionLocal(), player.id)
        print(f"\nCurrent game balance: ${player.balance:.2f}")
        print(f"Virtual wallet balance: ${virtual_wallet:.2f}")
        print(f"Current token conversion rate: {conversion_rate}")
        print("\nExchange Menu:")
        print("1. Deposit Money from Virtual Wallet")
        print("2. Withdraw Money to Virtual Wallet")
        print("3. Add Funds to Virtual Wallet")
        print("4. Set Token Conversion Rate")
        print("5. Return to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            amount = float(input("Enter amount to deposit from virtual wallet: $"))
            if amount > virtual_wallet:
                print("Insufficient funds in virtual wallet.")
            else:
                virtual_wallet -= amount
                # Ensure we have the latest player object with ID
                db = SessionLocal()
                player = get_player(db, player.username)
                db.close()
                player = deposit_to_player(player, amount)
                print(f"Deposited ${amount:.2f} to game balance.")
        elif choice == '2':
            amount = float(input("Enter amount to withdraw to virtual wallet: $"))
            if amount > player.balance:
                print("Insufficient funds in game balance.")
            else:
                player = withdraw_to_bank(player, amount)
                virtual_wallet += amount
                print(f"Withdrawn ${amount:.2f} to virtual wallet.")
        elif choice == '3':
            amount = float(input("Enter amount to add to virtual wallet: $"))
            virtual_wallet += amount
            print(f"Added ${amount:.2f} to virtual wallet.")
        elif choice == '4':
            rate = float(input("Enter new token conversion rate: "))
            update_token_conversion_rate(SessionLocal(), player.id, rate)
            print(f"Token conversion rate updated to {rate}")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

    return player  # Return the updated player object

def play_slot_machine(player, session):
    spin_reels, check_win, play_bonus_game = selected_model()
    spin_number = 0
    while True:
        spin_number += 1
        player.balance = get_player_balance(player)  # Update player balance from database
        print(f"\nCurrent balance: ${player.balance:.2f}")
        bet_amount = float(input("Enter your bet amount (or 0 to quit): $"))
        if bet_amount == 0:
            break

        if bet_amount > player.balance:
            print("Insufficient funds. Please enter a lower bet amount.")
            continue

        player = place_bet(player, bet_amount)

        outcome = spin_reels()
        points, max_payout, triggered_events, winning_paylines = check_win(outcome)
        winnings = points * bet_amount

        # Apply house edge
        winnings *= (1 - HOUSE_EDGE)

        if "BONUS" in triggered_events:
            bonus_win = play_bonus_game()
            winnings += bonus_win

        # Check for jackpot
        jackpot_win = check_jackpot_win(outcome)
        if jackpot_win:
            jackpot_amount = load_jackpot()
            winnings += jackpot_amount
            reset_jackpot()
            print(f"Congratulations! You won the jackpot of ${jackpot_amount:.2f}!")
        else:
            new_jackpot = increment_jackpot(bet_amount)
            print(f"Jackpot increased to ${new_jackpot:.2f}")

        player = add_winnings(player, winnings)
        record_spin(session.id, spin_number, bet_amount, str(outcome), winnings)

        print(f"Spin {spin_number}:")
        print(f"Bet: ${bet_amount:.2f}")
        print(f"Outcome: {outcome}")
        if winning_paylines:
            print(f"Winning lines: {', '.join(winning_paylines)}")
        print(f"Won: ${winnings:.2f}")
        print(f"New Balance: ${player.balance:.2f}")

    return player

def main_menu():
    print("Entering main menu")  # Debug print
    player, session = start_game()
    if not player or not session:
        print("Failed to start game session")  # Debug print
        return

    while True:
        player.balance = get_player_balance(player)  # Update player balance from database
        print(f"\nCurrent balance: ${player.balance:.2f}")
        print("\nMain Menu:")
        print("1. Play Slot Machine")
        print("2. Exchange Menu")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            player = play_slot_machine(player, session)
        elif choice == '2':
            player = exchange_menu(player)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

    end_game(session.id, player.balance)
    print(f"Thanks for playing! Your final balance is ${player.balance:.2f}")

if __name__ == "__main__":
    print("Starting main menu")  # Debug print
    main_menu()
    print("Script ended")  # Debug print
