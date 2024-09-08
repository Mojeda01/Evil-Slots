import json
import os
from sqlalchemy.orm import Session
from db_models import ReelConfiguration, SymbolPayout
from database import SessionLocal
import logging

CONFIG_FILE = 'slot_config.json'

# Default configuration
DEFAULT_CONFIG = {
    'reels': {
        'Reel1': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel2': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel3': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel4': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel5': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
    },
    'symbol_payouts': {
        'CHER': 2,  # pays 2x the bet amount
        'ONIO': 3,
        'CLOC': 4,
        'STAR': 5,
        'DIAMN': 10,
        'WILD': 15,
        'BONUS': 20,
        'SCAT': 25,
        'JACKP': 50
    }
}

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    config_path = CONFIG_FILE  # Use the constant defined at the top of the file
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        # File doesn't exist or is empty, create it with default config
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(config_path, 'r') as f:
        content = f.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update_probabilities(new_probabilities):
    db = SessionLocal()
    try:
        for reel, symbols in new_probabilities.items():
            reel_number = int(reel[4:])  # Extract number from 'Reel1', 'Reel2', etc.
            for symbol, probability in symbols.items():
                config = db.query(ReelConfiguration).filter(
                    ReelConfiguration.reel_number == reel_number,
                    ReelConfiguration.symbol == symbol
                ).first()
                if config:
                    config.probability = probability
                else:
                    new_config = ReelConfiguration(reel_number=reel_number, symbol=symbol, probability=probability)
                    db.add(new_config)
        db.commit()
    finally:
        db.close()

def get_reel_probabilities():
    db = SessionLocal()
    try:
        reels = {}
        for reel in range(1, 6):  # Assuming 5 reels
            reel_config = db.query(ReelConfiguration).filter(ReelConfiguration.reel_number == reel).all()
            reels[f'Reel{reel}'] = {config.symbol: float(config.probability) for config in reel_config}
        return reels
    finally:
        db.close()

def get_symbol_payouts():
    db = SessionLocal()
    try:
        payouts = db.query(SymbolPayout).all()
        return {payout.symbol: payout.payout for payout in payouts}
    finally:
        db.close()

def update_symbol_payouts(new_payouts):
    db = SessionLocal()
    try:
        for symbol, payout in new_payouts.items():
            symbol_payout = db.query(SymbolPayout).filter(SymbolPayout.symbol == symbol).first()
            if symbol_payout:
                symbol_payout.payout = payout
            else:
                new_symbol_payout = SymbolPayout(symbol=symbol, payout=payout)
                db.add(new_symbol_payout)
        db.commit()
    finally:
        db.close()

__all__ = ['get_reel_probabilities', 'update_probabilities', 'get_symbol_payouts', 'update_symbol_payouts']
