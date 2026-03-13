class Game:
    def __init__(self, best_of=5):
        self.best_of = best_of
        self.wins_needed = best_of // 2 + 1
        self.player_score = 0
        self.ai_score = 0
        self.round = 1
        self.history = []  # list of (player_move, ai_move, result)

    def play_round(self, player_move, ai_move):
        """Returns 'player', 'ai', or 'draw'"""
        result = self._determine_winner(player_move, ai_move)

        if result == "player":
            self.player_score += 1
        elif result == "ai":
            self.ai_score += 1

        self.history.append((player_move, ai_move, result))
        self.round += 1
        return result

    def _determine_winner(self, player, ai):
        if player == ai:
            return "draw"
        wins = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}
        return "player" if (player, ai) in wins else "ai"

    def is_over(self):
        """Returns 'player', 'ai', or None if game still going"""
        if self.player_score >= self.wins_needed:
            return "player"
        if self.ai_score >= self.wins_needed:
            return "ai"
        return None

    def reset(self):
        self.player_score = 0
        self.ai_score = 0
        self.round = 1
        self.history.clear()

    def get_status(self):
        return {
            "round": self.round,
            "best_of": self.best_of,
            "player_score": self.player_score,
            "ai_score": self.ai_score,
        }