import json

def load_wallet(file_name):
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Initialize wallet if it doesn't exist
        initial_wallet = {'balance': 0, 'tokens': 0}
        save_wallet(file_name, initial_wallet)
        return initial_wallet

def save_wallet(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

def transfer_funds(amount, from_wallet, to_wallet):
    if from_wallet['balance'] >= amount:
        from_wallet['balance'] -= amount
        to_wallet['balance'] += amount
        return True
    return False

def deposit_to_player(amount):
    bank_wallet = load_wallet('bank_wallet.json')
    player_wallet = load_wallet('player_wallet.json')
    
    if transfer_funds(amount, bank_wallet, player_wallet):
        save_wallet('bank_wallet.json', bank_wallet)
        save_wallet('player_wallet.json', player_wallet)
        print(f"Successfully deposited ${amount:.2f} to player wallet.")
        return True
    else:
        print("Insufficient funds in bank wallet.")
        return False

def convert_to_tokens(amount, exchange_rate):
    player_wallet = load_wallet('player_wallet.json')
    if player_wallet['balance'] >= amount:
        tokens = amount * exchange_rate
        player_wallet['balance'] -= amount
        player_wallet['tokens'] += tokens
        save_wallet('player_wallet.json', player_wallet)
        print(f"Converted ${amount:.2f} to {tokens} tokens.")
        return True
    else:
        print("Insufficient funds to convert to tokens.")
        return False

def convert_to_money(tokens, exchange_rate):
    player_wallet = load_wallet('player_wallet.json')
    if player_wallet['tokens'] >= tokens:
        amount = tokens / exchange_rate
        player_wallet['tokens'] -= tokens
        player_wallet['balance'] += amount
        save_wallet('player_wallet.json', player_wallet)
        print(f"Converted {tokens} tokens to ${amount:.2f}.")
        return True
    else:
        print("Insufficient tokens to convert to money.")
        return False

def place_bet(amount, use_tokens=False):
    player_wallet = load_wallet('player_wallet.json')
    if use_tokens:
        if player_wallet['tokens'] >= amount:
            player_wallet['tokens'] -= amount
            save_wallet('player_wallet.json', player_wallet)
            print(f"Bet of {amount} tokens placed successfully.")
            return True
    else:
        if player_wallet['balance'] >= amount:
            player_wallet['balance'] -= amount
            save_wallet('player_wallet.json', player_wallet)
            print(f"Bet of ${amount:.2f} placed successfully.")
            return True
    print("Insufficient funds in player wallet.")
    return False

def add_winnings(amount, add_tokens=False):
    player_wallet = load_wallet('player_wallet.json')
    if add_tokens:
        player_wallet['tokens'] += amount
        print(f"Winnings of {amount} tokens added to player wallet.")
    else:
        player_wallet['balance'] += amount
        print(f"Winnings of ${amount:.2f} added to player wallet.")
    save_wallet('player_wallet.json', player_wallet)

def get_player_balance(get_tokens=False):
    player_wallet = load_wallet('player_wallet.json')
    return player_wallet.get('tokens', 0) if get_tokens else player_wallet['balance']

def format_currency(amount):
    return f"${amount:.2f}"

def update_wallet(file_name, new_balance, new_tokens=None):
    wallet = load_wallet(file_name)
    wallet['balance'] = new_balance
    if new_tokens is not None:
        wallet['tokens'] = new_tokens
    save_wallet(file_name, wallet)

def withdraw_to_bank(amount):
    """Withdraw money from the player's balance to their bank account."""
    current_balance = get_player_balance()
    if amount <= 0:
        print("Invalid withdrawal amount. Please enter a positive number.")
        return False
    if amount > current_balance:
        print("Insufficient funds for withdrawal.")
        return False
    
    # Deduct the amount from the player's balance
    update_player_balance(-amount)
    
    # Update the bank wallet
    try:
        with open('bank_wallet.json', 'r') as f:
            bank_wallet = json.load(f)
        
        bank_wallet['balance'] += amount
        
        with open('bank_wallet.json', 'w') as f:
            json.dump(bank_wallet, f, indent=4)
        
        print(f"Successfully withdrew ${amount:.2f} to your bank account.")
        return True
    except Exception as e:
        print(f"Error updating bank wallet: {e}")
        # Rollback the player's balance update
        update_player_balance(amount)
        return False

def update_player_balance(amount):
    """Update the player's balance by adding the given amount (can be negative for deductions)."""
    current_balance = get_player_balance()
    new_balance = current_balance + amount
    # Save the new balance (implementation depends on how you're storing the balance)
    # For example, if you're using a file:
    with open('player_balance.txt', 'w') as f:
        f.write(str(new_balance))

def set_player_balance(balance, tokens=0):
    wallet = {"balance": balance, "tokens": tokens}
    with open('player_wallet.json', 'w') as f:
        json.dump(wallet, f, indent=4)
    print(f"Balance manually set to ${balance:.2f}")

# Example usage
if __name__ == "__main__":
    print(f"Initial player balance: {get_player_balance()}")
    print(f"Initial player tokens: {get_player_balance(get_tokens=True)}")
    deposit_to_player(100)
    print(f"Player balance after deposit: {get_player_balance()}")
    convert_to_tokens(50, 10)  # Convert $50 to tokens at a rate of 1:10
    print(f"Player balance after conversion: {get_player_balance()}")
    print(f"Player tokens after conversion: {get_player_balance(get_tokens=True)}")
    withdraw_to_bank(25)  # Withdraw $25 to bank wallet
    print(f"Player balance after withdrawal: {get_player_balance()}")