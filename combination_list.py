# Define winning combinations and their corresponding points

combinations = [
    # 5 of a kind
    {'symbols': ['CHER', 'CHER', 'CHER', 'CHER', 'CHER'], 'points': 1000, 'payout': 20},
    {'symbols': ['ONIO', 'ONIO', 'ONIO', 'ONIO', 'ONIO'], 'points': 750, 'payout': 15},
    {'symbols': ['CLOC', 'CLOC', 'CLOC', 'CLOC', 'CLOC'], 'points': 500, 'payout': 10},
    {'symbols': ['STAR', 'STAR', 'STAR', 'STAR', 'STAR'], 'points': 250, 'payout': 5},
    {'symbols': ['DIAMN', 'DIAMN', 'DIAMN', 'DIAMN', 'DIAMN'], 'points': 1500, 'payout': 30},

    # 4 of a kind
    {'symbols': ['CHER', 'CHER', 'CHER', 'CHER', '*'], 'points': 200, 'payout': 5},
    {'symbols': ['ONIO', 'ONIO', 'ONIO', 'ONIO', '*'], 'points': 150, 'payout': 3.75},
    {'symbols': ['CLOC', 'CLOC', 'CLOC', 'CLOC', '*'], 'points': 100, 'payout': 2.5},
    {'symbols': ['STAR', 'STAR', 'STAR', 'STAR', '*'], 'points': 50, 'payout': 1.25},
    {'symbols': ['DIAMN', 'DIAMN', 'DIAMN', 'DIAMN', '*'], 'points': 300, 'payout': 7.5},

    # 3 of a kind
    {'symbols': ['CHER', 'CHER', 'CHER', '*', '*'], 'points': 15, 'payout': 1},  # Changed payout to 1x
    {'symbols': ['ONIO', 'ONIO', 'ONIO', '*', '*'], 'points': 40, 'payout': 1},
    {'symbols': ['CLOC', 'CLOC', 'CLOC', '*', '*'], 'points': 30, 'payout': 0.75},
    {'symbols': ['STAR', 'STAR', 'STAR', '*', '*'], 'points': 20, 'payout': 0.5},
    {'symbols': ['DIAMN', 'DIAMN', 'DIAMN', '*', '*'], 'points': 75, 'payout': 1.875},

    # New special combinations
    {'symbols': ['WILD', 'WILD', 'WILD', '*', '*'], 'points': 500, 'payout': 10},
    {'symbols': ['WILD', 'WILD', '*', '*', '*'], 'points': 100, 'payout': 2},
    {'symbols': ['WILD', '*', '*', '*', '*'], 'points': 10, 'payout': 0.2},
    {'symbols': ['BONUS', 'BONUS', 'BONUS', '*', '*'], 'points': 200, 'payout': 5, 'trigger': 'bonus_game'},
    {'symbols': ['SCAT', 'SCAT', 'SCAT', '*', '*'], 'points': 0, 'payout': 0, 'trigger': 'free_spins'},
    {'symbols': ['JACKP', 'JACKP', 'JACKP', 'JACKP', 'JACKP'], 'points': 10000, 'payout': 200, 'trigger': 'jackpot'},
    {'symbols': ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN'], 'points': 150, 'payout': 3},
    {'symbols': ['DIAMN', 'DIAMN', '*', '*', '*'], 'points': 25, 'payout': 0.625},
    {'symbols': ['CHER', 'CHER', '*', '*', '*'], 'points': 15, 'payout': 0.375},
]