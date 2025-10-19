# gomoku_logic.py
import urandom

BOARD_SIZE = 15


class GomokuGame:
    def __init__(self):
        self.board = []
        self.game_over = False
        self.start_game()  # 自动初始化

    def start_game(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game_over = False
        return self.get_state("new_game", "游戏开始! 你是黑棋 (X)。")

    def get_state(self, status, message):
        return {
            "game": "gomoku",
            "status": status,
            "message": message,
            "board": self.board
        }

    # 玩家下棋
    def place_piece(self, x, y):
        if self.game_over:
            return self.get_state("game_over", "游戏已结束。请开新局。")

        if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
            return self.get_state("playing", "无效位置!")

        if self.board[y][x] != 0:
            return self.get_state("playing", "此位置已有棋子!")

        # 玩家 (1) 下棋
        self.board[y][x] = 1
        if self._check_win(1):
            self.game_over = True
            return self.get_state("player_win", "你赢了!")

        # AI (2) 下棋
        ai_move = self._ai_move()
        if ai_move:
            ax, ay = ai_move
            self.board[ay][ax] = 2
            if self._check_win(2):
                self.game_over = True
                return self.get_state("ai_win", "AI 赢了!")
        else:
            # 没有地方下了, 平局
            self.game_over = True
            return self.get_state("tie", "平局!")

        return self.get_state("playing", "轮到你了。")

    def _check_win(self, player):
        # 检查五子连珠
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] == player:
                    # 检查四个方向
                    if x + 4 < BOARD_SIZE and all(self.board[y][x + i] == player for i in range(5)): return True  # 水平
                    if y + 4 < BOARD_SIZE and all(self.board[y + i][x] == player for i in range(5)): return True  # 垂直
                    if x + 4 < BOARD_SIZE and y + 4 < BOARD_SIZE and all(
                        self.board[y + i][x + i] == player for i in range(5)): return True  # 右下
                    if x + 4 < BOARD_SIZE and y - 4 >= 0 and all(
                        self.board[y - i][x + i] == player for i in range(5)): return True  # 右上
        return False

    def _ai_move(self):
        # 简单 AI:
        # 1. 检查 AI (2) 能否一步获胜
        # 2. 检查 玩家 (1) 能否一步获胜 (如果能，则阻挡)
        # 3. 随机下在已有棋子的邻近位置

        empty_cells = []
        neighbors = set()  # 使用 set 避免重复

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] == 0:
                    empty_cells.append((x, y))

                    # 检查 AI (2) 是否能赢
                    self.board[y][x] = 2
                    if self._check_win(2):
                        return (x, y)  # 1. 获胜
                    self.board[y][x] = 0  # 撤销

                elif self.board[y][x] != 0:  # 是一个棋子
                    # 查找邻近的空位
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0: continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[ny][nx] == 0:
                                neighbors.add((nx, ny))

        # 检查 玩家 (1) 是否能赢 (阻挡)
        for x, y in empty_cells:
            self.board[y][x] = 1
            if self._check_win(1):
                self.board[y][x] = 0  # 撤销
                return (x, y)  # 2. 阻挡
            self.board[y][x] = 0  # 撤销

        # 3. 随机下在邻近位置
        if neighbors:
            return urandom.choice(list(neighbors))

        # 备用：如果棋盘是空的, 下在中间
        if not empty_cells:
            return None  # 平局
        if self.board[7][7] == 0:
            return (7, 7)

        # 最后的备用方案：随机下一个
        return urandom.choice(empty_cells)