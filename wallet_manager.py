from database import SessionLocal
from data_access import update_player_balance_in_db, get_player, update_token_conversion_rate, get_token_conversion_rate, update_player_balance

def place_bet(player, amount):
    db = SessionLocal()
    try:
        if player.balance >= amount:
            player.balance -= amount
            update_player_balance_in_db(db, player)
        else:
            print("Insufficient funds to place bet.")
    finally:
        db.close()
    return player

def add_winnings(player, amount):
    db = SessionLocal()
    try:
        player.balance += amount
        update_player_balance_in_db(db, player)
    finally:
        db.close()
    return player

def get_player_balance(player):
    db = SessionLocal()
    try:
        updated_player = get_player(db, player.username)
        return updated_player.balance
    finally:
        db.close()

def set_token_conversion_rate(player, rate):
    db = SessionLocal()
    try:
        update_token_conversion_rate(db, player.id, rate)
    finally:
        db.close()

def get_token_conversion_rate(player):
    db = SessionLocal()
    try:
        return get_token_conversion_rate(db, player.id)
    finally:
        db.close()

def deposit_to_player(player, amount):
    player.balance += amount
    update_player_balance(SessionLocal(), player.id, player.balance)
    return player

def withdraw_to_bank(player, amount):
    if player.balance >= amount:
        player.balance -= amount
        update_player_balance(SessionLocal(), player.id, player.balance)
    else:
        print("Insufficient funds in game balance.")
    return player