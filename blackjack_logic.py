# blackjack_logic.py
import urandom

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']  # 黑桃, 红心, 方片, 梅花


class BlackjackGame:
    def __init__(self):
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.status = "init"  # 'playing', 'player_win', 'dealer_win', 'player_bust', 'dealer_bust', 'tie'
        self.start_game()

    def _build_deck(self):
        """创建一副 52 张牌的牌组"""
        self.deck = []
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append({'rank': rank, 'suit': suit})

        # MicroPython 的 urandom.shuffle 直接在列表上操作
        urandom.shuffle(self.deck)

    def _deal_card(self):
        """发一张牌，如果牌堆空了则重新洗牌"""
        if len(self.deck) == 0:
            self._build_deck()
        return self.deck.pop()

    def _calculate_score(self, hand):
        """计算一手牌的分数，智能处理 A"""
        score = 0
        ace_count = 0

        for card in hand:
            rank = card['rank']
            if rank in ['J', 'Q', 'K']:
                score += 10
            elif rank == 'A':
                ace_count += 1
                score += 11  # 默认 A 为 11
            else:
                score += int(rank)

        # 处理 A (如果分数超过 21，将 A 从 11 变为 1)
        while score > 21 and ace_count > 0:
            score -= 10
            ace_count -= 1

        return score

    def start_game(self):
        """开始新游戏"""
        self._build_deck()
        self.player_hand = [self._deal_card(), self._deal_card()]
        self.dealer_hand = [self._deal_card(), self._deal_card()]
        self.status = 'playing'

        player_score = self._calculate_score(self.player_hand)
        dealer_score = self._calculate_score(self.dealer_hand)

        # 检查开局 (Blackjack)
        if player_score == 21:
            if dealer_score == 21:
                self.status = 'tie'  # 双方都是 Blackjack
            else:
                self.status = 'player_win'  # 玩家 Blackjack
        elif dealer_score == 21:
            self.status = 'dealer_win'  # 庄家 Blackjack

        return self.get_state()

    def hit(self):
        """玩家要牌"""
        if self.status != 'playing':
            return self.get_state()

        self.player_hand.append(self._deal_card())
        player_score = self._calculate_score(self.player_hand)

        if player_score > 21:
            self.status = "player_bust"
        elif player_score == 21:
            # 玩家拿到 21 点，自动停牌
            return self.stand()

        return self.get_state()

    def stand(self):
        """玩家停牌，轮到庄家行动"""
        if self.status != 'playing':
            return self.get_state()

        player_score = self._calculate_score(self.player_hand)
        dealer_score = self._calculate_score(self.dealer_hand)

        # 庄家逻辑: 必须在 17 点或以上时停牌 (包括软 17)
        while dealer_score < 17:
            self.dealer_hand.append(self._deal_card())
            dealer_score = self._calculate_score(self.dealer_hand)

        # 结算
        if dealer_score > 21:
            self.status = "dealer_bust"
        elif dealer_score > player_score:
            self.status = "dealer_win"
        elif player_score > dealer_score:
            self.status = "player_win"
        else:  # player_score == dealer_score
            self.status = "tie"

        return self.get_state()

    def _format_hand(self, hand):
        """辅助函数：将牌的字典格式化为字符串 (例如 'K♠')"""
        return [f"{card['rank']}{card['suit']}" for card in hand]

    def get_state(self):
        """向前端发送游戏状态"""
        player_score = self._calculate_score(self.player_hand)

        player_hand_display = self._format_hand(self.player_hand)
        dealer_hand_display = []
        dealer_score_display = 0

        if self.status == 'playing':
            # 游戏进行中，隐藏庄家第二张牌
            dealer_hand_display = [self._format_hand([self.dealer_hand[0]])[0], '??']
            # 只计算庄家明牌的分数
            dealer_score_display = self._calculate_score([self.dealer_hand[0]])
        else:
            # 游戏结束，显示所有牌
            dealer_hand_display = self._format_hand(self.dealer_hand)
            dealer_score_display = self._calculate_score(self.dealer_hand)

        return {
            "game": "blackjack",
            "player_hand": player_hand_display,  # e.g., ['A♥', '10♦']
            "player_score": player_score,
            "dealer_hand": dealer_hand_display,  # e.g., ['K♠', '??']
            "dealer_score": dealer_score_display,
            "status": self.status,
            "deck_size": len(self.deck)  # 额外信息
        }