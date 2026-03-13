import random
from collections import defaultdict

class AdaptiveAI:
    def __init__(self, difficulty="medium"):
        # How often AI uses prediction vs random
        self.predict_chance = {"easy": 0.2, "medium": 0.5, "hard": 0.9}
        self.difficulty = difficulty
        self.history = []  # player's past moves
        self.counters = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
        self.freq = defaultdict(lambda: defaultdict(int))  # bigram: prev -> next -> count

    def record(self, move):
        """Call this after every player move"""
        if self.history:
            prev = self.history[-1]
            self.freq[prev][move] += 1
        self.history.append(move)

    def predict_player(self):
        """Predict player's next move based on last move"""
        if not self.history:
            return random.choice(["rock", "paper", "scissors"])
        prev = self.history[-1]
        counts = self.freq[prev]
        if not counts:
            return random.choice(["rock", "paper", "scissors"])
        return max(counts, key=counts.get)

    def get_move(self):
        """Return AI's move"""
        if random.random() < self.predict_chance[self.difficulty]:
            predicted = self.predict_player()
            return self.counters[predicted]  # play counter to predicted move
        return random.choice(["rock", "paper", "scissors"])

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.history.clear()
        self.freq.clear()