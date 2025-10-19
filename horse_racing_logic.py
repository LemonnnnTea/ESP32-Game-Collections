# horse_racing_logic.py
import urandom


class HorseRacingGame:
    def __init__(self):
        self.num_horses = 4
        self.race_length = 50  # 赛道长度

    def start_race(self, bet_on_horse):
        positions = [0] * self.num_horses
        # race_log 会记录比赛的每一步
        race_log = []
        race_log.append(list(positions))  # 0 时刻的初始位置

        winner = -1

        while winner == -1:
            for i in range(self.num_horses):
                # 每匹马随机前进 1-4 步
                positions[i] += urandom.randint(1, 4)

                # 如果有马匹冲过终点线，且还没有产生冠军
                if positions[i] >= self.race_length and winner == -1:
                    winner = i  # 记录冠军

            race_log.append(list(positions))  # 记录这一轮的位置

            # 确保循环会停止
            if winner != -1:
                break

        # 比赛结束，计算结果
        if winner == bet_on_horse:
            result_msg = f"你赢了! {winner + 1} 号马获胜!"
        else:
            result_msg = f"你输了。 {winner + 1} 号马获胜。"

        return {
            "game": "horse_racing",
            "status": "finished",
            "race_log": race_log,  # 把完整的日志发给前端
            "winner": winner,
            "bet_on": bet_on_horse,
            "result_message": result_msg,
            "num_horses": self.num_horses
        }