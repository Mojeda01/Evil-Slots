# Slot Machine Algorithm Project

<p align="center">
  <img src="icon.png" alt="Slot Machine Simulation Project Icon" width="500">
</p>

**I MANAGED TO BREAK THIS PROJECT AND I AM TOO LAZY TO FIX IT, THE GUI IS FUCKED AND NOTHING WORKS!**

This project implements a slot machine reel algorithm without a graphical user interface. It includes supportive diagnostics tools to manipulate the algorithm's probabilities. In theory, this algorithm can be integrated with an actual slots game, as it produces reel results that can be exported to other applications, such as a GUI. This allows for the possibility of a purely graphical slots game that derives its reel choices from this algorithm, as it performs calculations that can be outputted in various formats.

## Components

### 1. Slot Machine Algorithm (reelAlgo.py)

<p align="center">
  <img src="slots.png" alt="Slot Machine Simulation Project Icon" width="500">
</p>

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
- 🟢 Integrated PostgreSQL database for storing game results
- 🟢 Implemented virtual wallet system for deposits and withdrawals

The script provides a text-based interface for playing the game, allowing users to place bets, spin the reels, and participate in bonus rounds. It now offers a more balanced and realistic slot machine experience with improved game economics and persistent data storage.

### 2. Diagnostics Tool (diagnostics_tool.py)

<p align="center">
  <img src="diagnostics.png" alt="Slot Machine Simulation Project Icon" width="800">
</p>

This tool provides real-time analysis, visualization of the slot machine's performance, and control over game probabilities and payouts. Features include:

- 🟢 Automatic updates based on changes in the database
- 🟢 Display of key statistics (total spins, winnings, average win, RTP)
- 🟢 Multiple charts for data visualization:
  - 🟢 Average Win per Spin
  - 🟢 Balance Over Time
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
- 🟢 Removed Bet Amount Distribution chart for improved performance

The tool uses DearPyGui for creating an interactive graphical interface with multiple charts arranged in a grid layout and intuitive controls for probability and payout adjustments.

### 3. Jackpot Manager (jackpot_manager.py)

This module manages the jackpot functionality for the slot machine game. It handles:

- 🟢 Initializing and loading the jackpot value from a file
- 🟢 Incrementing the jackpot based on bets placed
- 🟢 Saving the updated jackpot value
- 🟢 Checking for jackpot wins
- 🟢 Resetting the jackpot when necessary

The jackpot value is stored in a JSON file and increases by a configurable percentage of each bet placed.

### 4. Advanced Random Number Generator (advanced_rng.py)

This module implements a sophisticated random number generator specifically designed for the slot machine simulation. It uses the Mersenne Twister algorithm with enhanced seeding and AES encryption to provide high-quality, secure randomness while maintaining the desired probability distributions for each reel.

Key features include:

- **SlotMachineRNG Class**: Encapsulates the random number generation logic for the slot machine.
  - Uses Python's implementation of the Mersenne Twister algorithm.
  - Implements a robust seeding mechanism using multiple entropy sources.

- **Enhanced Seeding**: 
  - Combines current time (nanosecond precision), process ID, and random bytes from the operating system.
  - Uses SHA-256 hashing to create a 256-bit seed, ensuring high-quality initial randomness.

- **AES Encryption**:
  - Generates a unique 256-bit encryption key for each spin.
  - Encrypts random numbers using AES before symbol selection.
  - Decrypts numbers immediately before use, enhancing security without affecting probabilities.

- **Configurable Reel Generation**: 
  - Generates spin results based on the reel configuration provided in `slot_config.json`.
  - Maintains accurate symbol probabilities as defined in the configuration.

- **Symbol Mapping**: 
  - Implements a weighted random selection algorithm to map random numbers to symbols based on their defined probabilities.

- **Distribution Testing**: 
  - Includes a `test_distribution` function to verify the accuracy of symbol probabilities over a large number of spins.

This advanced RNG system ensures that the slot machine simulation maintains fairness and unpredictability while adhering to the configured probabilities for each symbol on each reel. The addition of AES encryption provides an extra layer of security, making it extremely difficult for potential attackers to predict or manipulate outcomes. This creates a solid foundation for a realistic, statistically accurate, and secure slot machine behavior.

Dependencies:
- cryptography library: Used for AES encryption and decryption.

### 5. Database Models (db_models.py)

This new component defines SQLAlchemy ORM models for:
- 🟢 Players: Stores user information and game statistics
- 🟢 Game Sessions: Tracks individual gaming sessions
- 🟢 Game Results: Records the outcome of each spin
- 🟢 Transactions: Logs all financial transactions

### 6. Data Access Layer (data_access.py)

Provides functions for interacting with the database:
- 🟢 Creating and retrieving players
- 🟢 Managing game sessions
- 🟢 Recording game results and transactions
- 🟢 Player authentication

### 7. Security Module (security.py)

Handles secure password management:
- 🟢 Password hashing using bcrypt
- 🟢 Password verification
- 🟢 Additional PBKDF2 hashing option

### 8. Database Management (database.py)

- 🟢 Sets up database connection using SQLAlchemy
- 🟢 Provides session management
- 🟢 Creates database tables based on ORM models

### 9. Database Backup and Recovery (db_recovery.py)

- 🟢 Implements database backup functionality
- 🟢 Provides database restoration capabilities

## Usage

1. Run `reelAlgo.py` to play the slot machine game.
2. Run `diagnostics_tool.py` to view real-time performance analytics and adjust game probabilities.
3. Use `database.py` to set up the database tables.
4. Run `test_database.py` to verify database operations.

## Dependencies

- 🟢 Python 3.x
- 🟢 NumPy
- 🟢 DearPyGui
- 🟢 SQLAlchemy
- 🟢 psycopg2-binary
- 🟢 passlib[bcrypt]
- 🟢 python-dotenv

## Files

- `reelAlgo.py`: Main slot machine game logic
- `diagnostics_tool.py`: Performance analysis, visualization tool, and probability control
- `jackpot_manager.py`: Jackpot management module
- `advanced_rng.py`: Advanced random number generation
- `db_models.py`: Database ORM models
- `data_access.py`: Database interaction functions
- `security.py`: Password hashing and verification
- `database.py`: Database setup and management
- `db_recovery.py`: Database backup and recovery
- `test_database.py`: Database operation tests
- `slot_config.json`: Stores reel probabilities and other game configuration settings

## Future Improvements

- 🟢 Implement a graphical user interface for the slot machine game
- 🟢 Enhance the diagnostics tool with more advanced analytics
- 🟢 Add more customization options for the slot machine configuration
- 🟢 Implement real-time synchronization between probability changes and the running game

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `sample.env` to `.env` and update with your database credentials
4. Run `python database.py` to set up the database

*A Project by: Marco Å. Ojeda*
