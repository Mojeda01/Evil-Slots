from sqlalchemy.orm import Session
from db_models import Jackpot
from database import SessionLocal
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def initialize_jackpot(initial_value=1000.0):
    db = SessionLocal()
    try:
        jackpot = db.query(Jackpot).first()
        if not jackpot:
            new_jackpot = Jackpot(value=initial_value)
            db.add(new_jackpot)
            db.commit()
            logger.info(f"Initialized jackpot with value: {initial_value}")
        else:
            logger.info(f"Jackpot already exists with value: {jackpot.value}")
    except Exception as e:
        logger.error(f"Error initializing jackpot: {e}")
        db.rollback()
    finally:
        db.close()

def load_jackpot():
    logger.debug("Attempting to load jackpot")
    db = SessionLocal()
    try:
        jackpot = db.query(Jackpot).first()
        if jackpot:
            logger.debug(f"Loaded jackpot: {jackpot.value}")
            return jackpot.value
        else:
            logger.warning("No jackpot found, initializing...")
            initialize_jackpot()
            return load_jackpot()
    except Exception as e:
        logger.error(f"Error loading jackpot: {e}")
        raise
    finally:
        db.close()

def save_jackpot(value):
    logger.debug(f"Attempting to save jackpot: {value}")
    db = SessionLocal()
    try:
        jackpot = db.query(Jackpot).first()
        if jackpot:
            jackpot.value = value
        else:
            new_jackpot = Jackpot(value=value)
            db.add(new_jackpot)
        db.commit()
        logger.debug("Jackpot saved successfully")
    except Exception as e:
        logger.error(f"Error saving jackpot: {e}")
        db.rollback()
    finally:
        db.close()

def increment_jackpot(bet_amount):
    logger.debug(f"Attempting to increment jackpot by {bet_amount * 0.01}")
    db = SessionLocal()
    try:
        jackpot = db.query(Jackpot).first()
        if jackpot:
            jackpot.value += bet_amount * 0.01  # Increment by 1% of bet
            db.commit()
            logger.debug(f"Jackpot incremented to: {jackpot.value}")
            return jackpot.value
        else:
            logger.warning("No jackpot found, initializing...")
            initialize_jackpot()
            return increment_jackpot(bet_amount)
    except Exception as e:
        logger.error(f"Error incrementing jackpot: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def reset_jackpot():
    logger.debug("Attempting to reset jackpot")
    save_jackpot(1000)  # Reset to initial amount
    return 1000

def check_jackpot_win(outcome, jackpot_symbol='JACKP', required_count=3):
    logger.debug(f"Checking for jackpot win with outcome: {outcome}")
    
    # Flatten the outcome list if it's nested
    flat_outcome = [symbol for reel in outcome for symbol in reel] if isinstance(outcome[0], list) else outcome
    
    # Count the number of jackpot symbols
    jackpot_count = flat_outcome.count(jackpot_symbol)
    
    is_jackpot_win = jackpot_count >= required_count
    logger.debug(f"Jackpot win: {is_jackpot_win}")
    
    return is_jackpot_win