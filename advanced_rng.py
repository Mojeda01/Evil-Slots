import random
import time
import os
import hashlib
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class SlotMachineRNG:
    """
    A class that implements a random number generator for a slot machine,
    using the Mersenne Twister algorithm with enhanced seeding.
    """

    def __init__(self):
        """
        Initialize the SlotMachineRNG with a Random object and seed it.
        """
        self.generator = random.Random()
        self.reseed()

    def reseed(self):
        """
        Reseed the random number generator using multiple sources of entropy.
        This method combines current time, process ID, and random bytes
        to create a unique and unpredictable seed.
        """
        # Get current time in nanoseconds
        current_time = time.time_ns()
        # Get the current process ID
        pid = os.getpid()
        # Get 16 random bytes from the operating system
        random_bytes = os.urandom(16)
        
        # Combine all sources of entropy into a single string
        seed_material = f"{current_time}{pid}{random_bytes.hex()}"
        # Create a 256-bit integer seed using SHA-256 hash
        seed = int(hashlib.sha256(seed_material.encode()).hexdigest(), 16)
        
        # Seed the random number generator
        self.generator.seed(seed)

    def _generate_encryption_key(self):
        """Generate a new encryption key for each spin."""
        return os.urandom(32)  # 256-bit key for AES

    def _encrypt_number(self, number, key):
        """Encrypt a number using AES."""
        backend = default_backend()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(str(number).encode()) + encryptor.finalize()
        return iv + encrypted

    def _decrypt_number(self, encrypted, key):
        """Decrypt a number using AES."""
        backend = default_backend()
        iv = encrypted[:16]
        ciphertext = encrypted[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return int(decrypted.decode())

    def generate_spin(self, reel_config):
        """
        Generate a complete spin result for all reels.
        
        :param reel_config: A dictionary containing the configuration for each reel
        :return: A list of lists, each inner list representing the symbols on one reel
        """
        result = []
        encryption_key = self._generate_encryption_key()
        for reel in reel_config.values():
            symbols = list(reel.keys())
            weights = list(reel.values())
            reel_result = self._generate_reel_spin(symbols, weights, encryption_key)
            result.append(reel_result)
        return result

    def _generate_reel_spin(self, symbols, weights, encryption_key):
        """
        Generate a spin result for a single reel.
        
        :param symbols: List of symbols on the reel
        :param weights: Corresponding weights (probabilities) for each symbol
        :param encryption_key: Encryption key for the spin
        :return: A list of 3 symbols representing the visible part of the reel
        """
        total_weight = sum(weights)
        reel_result = []
        for _ in range(3):  # Generate 3 symbols per reel
            number = self.generator.randint(1, total_weight)
            encrypted_number = self._encrypt_number(number, encryption_key)
            decrypted_number = self._decrypt_number(encrypted_number, encryption_key)
            symbol = self._map_number_to_symbol(decrypted_number, symbols, weights)
            reel_result.append(symbol)
        return reel_result

    def _map_number_to_symbol(self, number, symbols, weights):
        """
        Map a random number to a symbol based on the weights.
        
        :param number: Random number generated
        :param symbols: List of symbols
        :param weights: Corresponding weights for each symbol
        :return: The selected symbol
        """
        cumulative_weight = 0
        for symbol, weight in zip(symbols, weights):
            cumulative_weight += weight
            if number <= cumulative_weight:
                return symbol
        return symbols[-1]  # Fallback to last symbol (should never happen)

def test_distribution(rng, reel_config, num_spins=10000):
    """
    Test the distribution of symbols over a large number of spins.
    
    :param rng: SlotMachineRNG instance
    :param reel_config: Reel configuration dictionary
    :param num_spins: Number of spins to simulate (default 10000)
    """
    symbol_counts = {symbol: 0 for reel in reel_config.values() for symbol in reel}
    total_symbols = num_spins * 3 * len(reel_config)

    for _ in range(num_spins):
        spin_result = rng.generate_spin(reel_config)
        for reel in spin_result:
            for symbol in reel:
                symbol_counts[symbol] += 1

    print("Symbol Distribution:")
    for symbol, count in symbol_counts.items():
        print(f"{symbol}: {count / total_symbols:.4f}")

# Example usage and test
if __name__ == "__main__":
    # Create an instance of SlotMachineRNG
    rng = SlotMachineRNG()
    
    # Load reel configuration from slot_config.json
    with open('slot_config.json', 'r') as f:
        config = json.load(f)
        reel_config = config['reels']

    # Run a distribution test
    test_distribution(rng, reel_config)

    # Example of generating a single spin
    spin_result = rng.generate_spin(reel_config)
    print("\nSample Spin Result:")
    for i, reel in enumerate(spin_result, 1):
        print(f"Reel {i}: {reel}")
