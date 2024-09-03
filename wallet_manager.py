import json

def load_wallet(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

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
        print(f"Successfully deposited {amount} to player wallet.")
    else:
        print("Insufficient funds in bank wallet.")

def place_bet(amount):
    player_wallet = load_wallet('player_wallet.json')
    if player_wallet['balance'] >= amount:
        player_wallet['balance'] -= amount
        save_wallet('player_wallet.json', player_wallet)
        print(f"Bet of {amount} placed successfully.")
        return True
    else:
        print("Insufficient funds in player wallet.")
        return False

def add_winnings(amount):
    player_wallet = load_wallet('player_wallet.json')
    player_wallet['balance'] += amount
    save_wallet('player_wallet.json', player_wallet)
    print(f"Winnings of {amount} added to player wallet.")

def get_player_balance():
    player_wallet = load_wallet('player_wallet.json')
    return player_wallet['balance']

# Example usage
if __name__ == "__main__":
    print(f"Initial player balance: {get_player_balance()}")
    deposit_to_player(100)
    print(f"Player balance after deposit: {get_player_balance()}")
    if place_bet(50):
        print(f"Player balance after betting: {get_player_balance()}")
        add_winnings(75)
        print(f"Player balance after winning: {get_player_balance()}")