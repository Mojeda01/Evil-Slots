# Slot Machine Simulation Project

<p align="center">
  <img src="icon.png" alt="Slot Machine Simulation Project Icon" width="500">
</p>

This project simulates a slot machine game with a graphical user interface and a diagnostics tool for performance analysis and game configuration.

## Components

### 1. Slot Machine Algorithm (reelAlgo.py)

This script implements the core logic of the slot machine game. Key features include:

- 🟢 Reel spinning mechanism with configurable symbol probabilities
- 🟢 Multiple paylines for win calculation
- 🟢 Bonus game functionality with adjustable trigger frequency
- 🟢 Currency and token management
- 🟢 Jackpot system integration
- 🟢 Logging of game results for analysis
- 🟢 Implemented house edge for long-term game balance
- 🟢 Maximum bet limit to prevent excessive wagering
- 🟢 Enhanced win calculation considering bet amount and house edge
- 🟢 Improved random selection of symbols based on configured probabilities
- 🟢 Removed inaccurate in-game RTP calculation for more realistic gameplay
- 🟢 Updated main menu for streamlined user interaction

The script provides a text-based interface for playing the game, allowing users to place bets, spin the reels, and participate in bonus rounds. It now offers a more balanced and realistic slot machine experience with improved game economics.

### 2. Diagnostics Tool (diagnostics_tool.py)
<p align="center">
  <img src="diagnostics.png" alt="Slot Machine Simulation Project Icon" width="800">
</p>
This tool provides real-time analysis, visualization of the slot machine's performance, and control over game probabilities and payouts. Features include:

- 🟢 Automatic updates based on changes in the log file
- 🟢 Display of key statistics (total spins, winnings, average win, RTP)
- 🟢 Multiple charts for data visualization:
  - 🟢 Average Win per Spin
  - 🟢 Balance Over Time
  - 🟢 Bet Amount Distribution
  - 🟢 Points Won Over Time
  - 🟢 Winnings Breakdown
  - 🟢 Jackpot Progression
  - 🟢 Win Frequency
  - 🟢 RTP Over Time
  - 🟢 Bonus Trigger Frequency
- 🟢 Probability Control:
  - 🟢 View and adjust symbol probabilities for each reel
  - 🟢 Apply probability settings from one reel to all reels for quick configuration
  - 🟢 Save updated probabilities to directly affect the game's behavior
- 🟢 Payout Control:
  - 🟢 View and adjust symbol payouts
  - 🟢 Modify payouts for individual symbols or combinations
  - 🟢 Save updated payouts to immediately impact game economics

The tool uses DearPyGui for creating an interactive graphical interface with multiple charts arranged in a grid layout and intuitive controls for probability and payout adjustments.

### 3. Jackpot Manager (jackpot_manager.py)

This module manages the jackpot functionality for the slot machine game. It handles:

- 🟢 Initializing and loading the jackpot value from a file
- 🟢 Incrementing the jackpot based on bets placed
- 🟢 Saving the updated jackpot value
- 🟢 Checking for jackpot wins
- 🟢 Resetting the jackpot when necessary

The jackpot value is stored in a JSON file and increases by a configurable percentage of each bet placed.

## Usage

1. Run `reelAlgo.py` to play the slot machine game.
2. Run `diagnostics_tool.py` to view real-time performance analytics and adjust game probabilities.

## Dependencies

- 🟢 Python 3.x
- 🟢 NumPy
- 🟢 DearPyGui

## Files

- `reelAlgo.py`: Main slot machine game logic
- `diagnostics_tool.py`: Performance analysis, visualization tool, and probability control
- `jackpot_manager.py`: Jackpot management module
- `logs.json`: Game result logs (generated by reelAlgo.py)
- `jackpot.json`: Stores the current jackpot value
- `slot_config.json`: Stores reel probabilities and other game configuration settings

## Future Improvements

- 🟢 Implement a graphical user interface for the slot machine game
- 🟢 Enhance the diagnostics tool with more advanced analytics
- 🟢 Add more customization options for the slot machine configuration
- 🟢 Implement real-time synchronization between probability changes and the running game