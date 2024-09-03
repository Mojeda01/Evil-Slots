# Define winning combinations and their corresponding points

combinations = [
    # 5 of a kind
    {'symbols': ['CHER', 'CHER', 'CHER', 'CHER', 'CHER'], 'points': 1000},
    {'symbols': ['ONIO', 'ONIO', 'ONIO', 'ONIO', 'ONIO'], 'points': 750},
    {'symbols': ['CLOC', 'CLOC', 'CLOC', 'CLOC', 'CLOC'], 'points': 500},
    {'symbols': ['STAR', 'STAR', 'STAR', 'STAR', 'STAR'], 'points': 250},
    {'symbols': ['DIAMN', 'DIAMN', 'DIAMN', 'DIAMN', 'DIAMN'], 'points': 1500},

    # 4 of a kind
    {'symbols': ['CHER', 'CHER', 'CHER', 'CHER', '*'], 'points': 200},
    {'symbols': ['ONIO', 'ONIO', 'ONIO', 'ONIO', '*'], 'points': 150},
    {'symbols': ['CLOC', 'CLOC', 'CLOC', 'CLOC', '*'], 'points': 100},
    {'symbols': ['STAR', 'STAR', 'STAR', 'STAR', '*'], 'points': 50},
    {'symbols': ['DIAMN', 'DIAMN', 'DIAMN', 'DIAMN', '*'], 'points': 300},

    # 3 of a kind
    {'symbols': ['CHER', 'CHER', 'CHER', '*', '*'], 'points': 50},
    {'symbols': ['ONIO', 'ONIO', 'ONIO', '*', '*'], 'points': 40},
    {'symbols': ['CLOC', 'CLOC', 'CLOC', '*', '*'], 'points': 30},
    {'symbols': ['STAR', 'STAR', 'STAR', '*', '*'], 'points': 20},
    {'symbols': ['DIAMN', 'DIAMN', 'DIAMN', '*', '*'], 'points': 75},

    # New special combinations
    {'symbols': ['WILD', 'WILD', 'WILD', '*', '*'], 'points': 500},
    {'symbols': ['WILD', 'WILD', '*', '*', '*'], 'points': 100},
    {'symbols': ['WILD', '*', '*', '*', '*'], 'points': 10},
    {'symbols': ['BONUS', 'BONUS', 'BONUS', '*', '*'], 'points': 200, 'trigger': 'bonus_game'},
    {'symbols': ['SCAT', 'SCAT', 'SCAT', '*', '*'], 'points': 0, 'trigger': 'free_spins'},
    {'symbols': ['JACKP', 'JACKP', 'JACKP', 'JACKP', 'JACKP'], 'points': 10000, 'trigger': 'jackpot'},
    {'symbols': ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN'], 'points': 150},
    {'symbols': ['DIAMN', 'DIAMN', '*', '*', '*'], 'points': 25},
    {'symbols': ['CHER', 'CHER', '*', '*', '*'], 'points': 15},
]