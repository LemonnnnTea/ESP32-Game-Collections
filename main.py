# main.py
from microwebsrv import MicroWebSrv
import json
import _thread

# 导入我们的游戏逻辑
from blackjack_logic import BlackjackGame
from slots_logic import SlotsGame
from guess_number_logic import GuessNumberGame  # 新增
from horse_racing_logic import HorseRacingGame  # 新增
from gomoku_logic import GomokuGame  # 新增

# 我们需要为每个连接的客户端（每个浏览器）保存一个游戏实例
client_games = {}


# =================================================
# WebSocket 回调函数
# =================================================

def _acceptWebSocketCallback(webSocket, httpClient):
    print("WS ACCEPTED")
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.ClosedCallback = _closedCallback

    # 为这个新客户端初始化所有游戏
    client_games[webSocket] = {
        "blackjack": BlackjackGame(),  # <-- 修改这里：在连接时就创建
        "slots": SlotsGame(),
        "guess_number": GuessNumberGame(),
        "gomoku": None,
        "horse_racing": HorseRacingGame()
    }


def _recvTextCallback(webSocket, msg):
    print(f"WS RECV: {msg}")
    try:
        data = json.loads(msg)
        game_type = data.get("game")
        action = data.get("action")

        response = {}

        if game_type == "blackjack":
            # ... (21点逻辑不变) ...
            game_instance = client_games[webSocket].get("blackjack")

            if action == "start":
                # "start" 动作现在只是简单地调用 start_game() 方法
                response = game_instance.start_game()
            elif game_instance and action == "hit":
                response = game_instance.hit()
            elif game_instance and action == "stand":
                response = game_instance.stand()

        elif game_type == "slots":
            # ... (老虎机逻辑不变) ...
            game_instance = client_games[webSocket].get("slots")
            if action == "spin":
                response = game_instance.spin()
            elif action == "get_state":
                response = game_instance.get_state()

        # --- 新增游戏逻辑 ---

        elif game_type == "guess_number":
            game_instance = client_games[webSocket].get("guess_number")
            if action == "guess":
                number = int(data.get("value", 0))
                response = game_instance.guess(number)
            elif action == "start":
                response = game_instance.start_game()

        elif game_type == "gomoku":
            game_instance = client_games[webSocket].get("gomoku")
            if action == "start":
                game_instance = GomokuGame()
                client_games[webSocket]["gomoku"] = game_instance
                response = game_instance.start_game()
            elif game_instance and action == "place":
                x = int(data.get("x", 0))
                y = int(data.get("y", 0))
                response = game_instance.place_piece(x, y)

        elif game_type == "horse_racing":
            game_instance = client_games[webSocket].get("horse_racing")
            if action == "start":
                bet_on = int(data.get("bet", 0))
                response = game_instance.start_race(bet_on)
        # --- 新增结束 ---

        # 将游戏状态发回给客户端
        webSocket.SendText(json.dumps(response))

    except Exception as e:
        print(f"WS Error: {e}")


def _closedCallback(webSocket):
    print("WS CLOSED")
    # 清理客户端的游戏实例
    if webSocket in client_games:
        del client_games[webSocket]


# =================================================
# 启动服务器 (不变)
# =================================================

print("正在启动 Web 服务器...")

srv = MicroWebSrv(webPath='/www')
srv.MaxWebSocketRecvLen = 256
srv.WebSocketThreaded = True
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
srv.Start(threaded=True)

print("服务器已启动！")