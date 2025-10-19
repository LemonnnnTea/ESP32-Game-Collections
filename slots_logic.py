import urandom

symbols = ['🍒', '🍋', '🍊', '🍉', '🔔', '⭐', '7️⃣']


class SlotsGame:
    def __init__(self):
        self.reels = ['?', '?', '?']
        self.credits = 100
        self.last_win = 0

    def spin(self):
        if self.credits < 1:
            return self.get_state("no_credits")

        self.credits -= 1  # 每次旋转花费1个点数

        # 随机旋转
        self.reels = [
            urandom.choice(symbols),
            urandom.choice(symbols),
            urandom.choice(symbols)
        ]

        # 检查是否中奖 (简化)
        if self.reels[0] == self.reels[1] == self.reels[2]:
            if self.reels[0] == '7️⃣':
                self.last_win = 100
            else:
                self.last_win = 20
        elif self.reels[0] == self.reels[1] or self.reels[1] == self.reels[2]:
            self.last_win = 5
        else:
            self.last_win = 0

        self.credits += self.last_win

        return self.get_state("spun")

    def get_state(self, status="ready"):
        return {
            "game": "slots",
            "reels": self.reels,
            "credits": self.credits,
            "last_win": self.last_win,
            "status": status
        }