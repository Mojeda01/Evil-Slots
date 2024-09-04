# Author: @marco.oj
# Description: This module manages the jackpot functionality for a slot machine game.
# It handles initializing, loading, saving, incrementing, and resetting the jackpot,
# as well as checking for jackpot wins. The jackpot value is stored in a JSON file
# and increases by a percentage of each bet placed.

import json
import os

JACKPOT_FILE = 'jackpot.json'
JACKPOT_INCREMENT_RATE = 0.02  # 2% of each bet

def initialize_jackpot(initial_value=1000):
    if not os.path.exists(JACKPOT_FILE):
        with open(JACKPOT_FILE, 'w') as f:
            json.dump({'jackpot': initial_value}, f)
        print(f"Created {JACKPOT_FILE} with initial jackpot of {initial_value}")

def load_jackpot():
    if not os.path.exists(JACKPOT_FILE):
        initialize_jackpot()
    
    with open(JACKPOT_FILE, 'r') as f:
        return json.load(f)['jackpot']

def save_jackpot(value):
    with open(JACKPOT_FILE, 'w') as f:
        json.dump({'jackpot': value}, f)

def increment_jackpot(bet_amount):
    current_jackpot = load_jackpot()
    new_jackpot = current_jackpot + (bet_amount * JACKPOT_INCREMENT_RATE)
    save_jackpot(new_jackpot)
    return new_jackpot

def reset_jackpot():
    save_jackpot(1000)  # Reset to initial amount
    return 1000

def check_jackpot_win(result):
    # Example: Win jackpot if all symbols are JACKP
    return all(symbol == 'JACKP' for row in result for symbol in row)