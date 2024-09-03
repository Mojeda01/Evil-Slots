import numpy as np

# 1. Define game elememnts
# SYMBOLS LIST
sym = ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN']

def selected_model():

    # Reels configuration: Defining probabilities for each symbol on each reel
    reels = {
        'Reel1':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 1
        'Reel2':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 2
        'Reel3':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 3
        'Reel4':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 4
        'Reel5':{sym[0]:5,sym[1]:4,sym[2]:3,sym[3]:2,sym[4]:1}, # Weights for Reel 5
    }
    
    # Step 2: Develop Initial spin_reels() Function
    def spin_reels():
        """Simulates spinning of the reels using weighted random selection with numpy."""
        reel_results = []

        for reel_name, reel in reels.items():
            # Get symbols and their corresponding weights
            symbols = list(reel.keys())
            weights = list(reel.values())

            # Use numpy's random.choice to select a symbol based on weights
            selected_symbol = np.random.choice(symbols, p=np.array(weights) / sum(weights))
            reel_results.append(selected_symbol)
        return reel_results
    
    print("Spinning the reels...")
    result = spin_reels()
    print(f'Result: {result[0]} | {result[1]} | {result[2]} | {result[3]} | {result[4]}')

    # WE HAVE NOT ACTUALLY TOLD THE PROGRAM IF ANY COMBINATION GIVES ANY POINTS
    # SO THE PROGRAM DOES NOT KNOW; IT ONLY JUST DISPLAYS THE RESULTS! :D


selected_model()