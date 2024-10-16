# Goals for Project
1. Game Mechanics:
    - [X] Implement multiple paylines (e.g., diagonal or zigzag patterns).
    - [X] Add a progressive jackpot feature.
    - [X]Create bonus rounds or mini-games triggered by special symbol combinations.
2. Expanded Wallet System:
    - [X] Add a currency exchange feature (eg., convert real money to game tokens).
    - [X] Implement different bet sizes and adjusts payouts accordingly.
3. Testing and balancing:
    - [X] Develop a simulation to test the game's payout rate over many spins.
    - [X] Fine-tune the probabilities and payouts to achieve desired return-to-player (RTP) rates.
4. ReelAlgo.py - Make it more customizable:
    - [X] Option to control the probability of each symbol on each reel.
    - [X] Option to control the payout for each symbol combination.
5. Backend Development - Added more points to this section below:
    - [X] 2. Create a server to handle player accounts and transactions securely.
    - [X] 1. Implement a database to store player data and game statistics.
    - [ ] 3. Add probability control to the PostGreSQL database. and making it adjustable in the dearpygui interface.
6. AI and Machine Learning:
    - [ ] Use machine learning to analyze player behavior and personalize the gaming experience.
7. Game Variations:
    - [ ] Add different themes or "machines" with unique symbols and payouts
    - [ ] Implement multi-player features or tournaments.
8. Compliance and responsile gaming:
    - [ ] Implement features to promote responsible gaming (e.g., spending limits, self-exclusion).
    - [ ] Research and comply with relevant gaming regulations in your target market.
***
# Building out goals more specifically
## 5. Backend Development
### 5.1 Implement a database to store player data and game statistics
- [ ] Choose a database system (e.g., PostgreSQL for relational data, MongoDB for flexible schema)
- [ ] Design database schema
  - [ ] Player table (id, username, email, password_hash, balance, created_at, last_login)
  - [ ] Transactions table (id, player_id, amount, type, timestamp)
  - [ ] GameSessions table (id, player_id, start_time, end_time, initial_balance, final_balance)
  - [ ] GameResults table (id, session_id, spin_number, bet_amount, outcome, winnings)
- [ ] Set up database connection in the application
- [ ] Implement data access layer (DAL) to interact with the database
- [ ] Create database backup and recovery procedures
- [ ] Implement data encryption for sensitive information

### 5.2 Security Measures
- [ ] Implement input validation and sanitization to prevent SQL injection and XSS attacks
- [ ] Set up proper error handling and logging
- [ ] Conduct regular security audits and penetration testing
- [ ] Implement multi-factor authentication for added security
- [ ] Use secure password hashing (e.g., bcrypt)
- [ ] Implement rate limiting and request validation to prevent abuse