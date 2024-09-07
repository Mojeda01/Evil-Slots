from sqlalchemy.orm import Session
from db_models import Player, GameSession, GameResult, Transaction
from datetime import datetime
from security import get_password_hash, verify_password  # Add this import

def create_player(db: Session, username: str, email: str, password: str, initial_balance: float = 0.0):
    hashed_password = get_password_hash(password)
    player = Player(
        username=username,
        email=email,
        password_hash=hashed_password,
        balance=initial_balance,
        token_conversion_rate=1.0,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
        total_spins=0,
        total_winnings=0.0
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def get_player(db: Session, identifier):
    if isinstance(identifier, int):
        return db.query(Player).filter(Player.id == identifier).first()
    elif isinstance(identifier, str):
        return db.query(Player).filter(Player.username == identifier).first()
    else:
        raise ValueError("Identifier must be either an integer (id) or a string (username)")

def update_player_balance(db: Session, player_id: int, new_balance: float):
    player = get_player(db, player_id)
    if player:
        player.balance = new_balance
        db.commit()
        db.refresh(player)
        return player
    return None

def create_game_session(db: Session, player_id: int, initial_balance: float):
    session = GameSession(player_id=player_id, initial_balance=initial_balance)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def end_game_session(db: Session, session_id: int, final_balance: float):
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if session:
        session.end_time = datetime.utcnow()
        session.final_balance = final_balance
        db.commit()
        db.refresh(session)
    return session

def record_game_result(db: Session, session_id: int, spin_number: int, bet_amount: float, outcome: str, winnings: float):
    result = GameResult(
        session_id=session_id,
        spin_number=spin_number,
        bet_amount=bet_amount,
        outcome=outcome,
        winnings=winnings
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

def record_transaction(db: Session, player_id: int, amount: float, transaction_type: str):
    transaction = Transaction(player_id=player_id, amount=amount, type=transaction_type)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def authenticate_player(db: Session, username: str, password: str):
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        return False
    if not verify_password(password, player.password_hash):
        return False
    return player

def update_player_balance_in_db(db: Session, player):
    db_player = db.query(Player).filter(Player.id == player.id).first()
    if db_player:
        db_player.balance = player.balance
        db.commit()
        db.refresh(db_player)
    return db_player

def update_token_conversion_rate(db: Session, player_id: int, new_rate: float) -> None:
    player = db.query(Player).filter(Player.id == player_id).first()
    if player:
        player.token_conversion_rate = new_rate
        db.commit()

def get_token_conversion_rate(db: Session, player_id: int) -> float:
    player = db.query(Player).filter(Player.id == player_id).first()
    if player and player.token_conversion_rate is not None:
        return player.token_conversion_rate
    return 1.0  # Default conversion rate if player not found or rate not set

# Add more data access functions as needed
