import json
import os

CONFIG_FILE = 'slot_config.json'

# Default configuration
DEFAULT_CONFIG = {
    'reels': {
        'Reel1': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel2': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel3': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel4': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
        'Reel5': {s: 1 for s in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']},
    }
}

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
    config = load_config()
    config['reels'] = new_probabilities
    save_config(config)

def get_reel_probabilities():
    config = load_config()
    return config['reels']
