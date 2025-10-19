# guess_number_logic.py
import urandom


class GuessNumberGame:
    def __init__(self):
        self.secret_number = 0
        self.guesses = 0
        self.start_game()

    def start_game(self):
        self.secret_number = urandom.randint(1, 100)
        self.guesses = 0
        return self.get_state("new_game", "我猜了一个 1-100 之间的数字。")

    def guess(self, number):
        self.guesses += 1
        if number < self.secret_number:
            return self.get_state("playing", f"太低了! (已猜{self.guesses}次)")
        elif number > self.secret_number:
            return self.get_state("playing", f"太高了! (已猜{self.guesses}次)")
        else:
            msg = f"恭喜! 猜对了! 答案是 {self.secret_number}。你用了 {self.guesses} 次。"
            return self.get_state("correct", msg)

    def get_state(self, status, message):
        return {
            "game": "guess_number",
            "status": status,
            "message": message,
            "guesses": self.guesses
        }