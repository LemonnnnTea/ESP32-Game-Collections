// 注意：这个 JS 文件将被两个 HTML 页面共享
// 我们将在页面加载时确定要连接哪个游戏

let ws;

function connectWebSocket(gameType) {
    const gateway = `ws://${window.location.host}/ws`;
    ws = new WebSocket(gateway);

    ws.onopen = () => {
        console.log('WebSocket 已连接');
        // 连接成功后，根据游戏类型发送初始化指令
        if (gameType === 'blackjack') {
            sendMessage({ game: 'blackjack', action: 'start' });
        } else if (gameType === 'slots') {
            sendMessage({ game: 'slots', action: 'get_state' });
        }
    };

    ws.onmessage = (event) => {
        console.log('收到消息:', event.data);
        try {
            const data = JSON.parse(event.data);
            if (data.game === 'blackjack') {
                updateBlackjackUI(data);
            } else if (data.game === 'slots') {
                updateSlotsUI(data);
            }
            // --- 新增 ---
            else if (data.game === 'guess_number') {
                updateGuessNumberUI(data);
            } else if (data.game === 'horse_racing') {
                updateHorseRacingUI(data);
            } else if (data.game === 'gomoku') {
                updateGomokuUI(data);
            }
        } catch (e) {
            console.error('解析JSON失败:', e);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket 已断开');
        // 可以在这里尝试重连
        document.getElementById('status').innerText = '连接已断开。请刷新页面。';
    };
}

// 统一的发送消息函数
function sendMessage(message) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
    }
}

// =================================================
// 21点 专用的 UI 更新
// =================================================
function updateBlackjackUI(state) {
    // 渲染手牌
    renderHand(document.getElementById('player-hand'), state.player_hand);
    renderHand(document.getElementById('dealer-hand'), state.dealer_hand);

    // 更新分数
    document.getElementById('player-score').innerText = state.player_score;
    document.getElementById('dealer-score').innerText = state.dealer_score;

    // 更新状态
    const statusEl = document.getElementById('status');
    const hitBtn = document.getElementById('btn-hit');
    const standBtn = document.getElementById('btn-stand');

    hitBtn.disabled = true;
    standBtn.disabled = true;

    switch(state.status) {
        case 'playing':
            statusEl.innerText = "请选择：要牌 (Hit) 或 停牌 (Stand)";
            hitBtn.disabled = false;
            standBtn.disabled = false;
            break;
        case 'player_bust':
            statusEl.innerText = "你爆了! (Bust) 庄家胜利。";
            break;
        case 'dealer_bust':
            statusEl.innerText = "庄家爆了! 你赢了!";
            break;
        case 'player_win':
            statusEl.innerText = "你赢了!";
            break;
        case 'dealer_win':
            statusEl.innerText = "庄家胜利。";
            break;
        case 'tie':
            statusEl.innerText = "平局 (Tie)。";
            break;
    }
}

// 渲染纸牌的辅助函数
function renderHand(element, hand) {
    element.innerHTML = ''; // 清空
    hand.forEach(cardStr => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';

        // cardStr 可能是 "K♠" 或 "10♦" 或 "??"
        if (cardStr === '??') {
            cardDiv.classList.add('hidden');
            cardDiv.innerText = '?';
        } else {
            // 提取花色和点数
            const suit = cardStr.slice(-1); // '♠', '♥', '♦', '♣'
            const rank = cardStr.slice(0, -1); // 'K', '10', 'A'

            cardDiv.innerText = rank + '\n' + suit;

            // 根据花色添加颜色
            if (suit === '♥' || suit === '♦') {
                cardDiv.classList.add('red');
            }
        }
        element.appendChild(cardDiv);
    });
}


// =================================================
// 老虎机 专用的 UI 更新
// =================================================
function updateSlotsUI(state) {
    document.getElementById('reel1').innerText = state.reels[0];
    document.getElementById('reel2').innerText = state.reels[1];
    document.getElementById('reel3').innerText = state.reels[2];

    document.getElementById('credits-display').innerText = `点数: ${state.credits}`;

    const statusEl = document.getElementById('status');
    if (state.last_win > 0) {
        statusEl.innerText = `恭喜! 赢得 ${state.last_win} 点!`;
    } else if (state.status === 'spun') {
        statusEl.innerText = "再试一次!";
    } else if (state.status === 'no_credits') {
        statusEl.innerText = "点数不足!";
    } else {
         statusEl.innerText = "点击 '旋转' 开始游戏";
    }

    // 可以在这里加一个简单的 CSS 动画来模拟“旋转”
    const reels = document.querySelectorAll('.reel');
    reels.forEach(reel => {
        reel.style.animation = 'none';
        reel.offsetHeight; // 触发重绘
        reel.style.animation = 'spinAnimation 0.5s ease-out';
    });
}

// 在 style.css 中加入这个动画
/*
@keyframes spinAnimation {
    0% { transform: translateY(-30px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}
*/

function updateGuessNumberUI(state) {
    const statusEl = document.getElementById('status');
    const guessInput = document.getElementById('guess-input');
    const guessBtn = document.getElementById('btn-guess');

    statusEl.innerText = state.message;

    if (state.status === 'correct') {
        guessInput.disabled = true;
        guessBtn.disabled = true;
    } else {
        guessInput.disabled = false;
        guessBtn.disabled = false;
        guessInput.value = '';
        guessInput.focus();
    }
}

// =================================================
// 赛马 专用的 UI 更新
// =================================================
let raceAnimationInterval = null;

function updateHorseRacingUI(state) {
    if (state.status === 'finished') {
        // 禁用投注按钮
        document.querySelectorAll('.bet-controls button').forEach(b => b.disabled = true);

        const log = state.race_log;
        const numHorses = state.num_horses;
        const trackLength = 100; // 100% 宽度
        const maxPos = state.race_log[state.race_log.length - 1][state.winner];

        let turn = 0;

        if (raceAnimationInterval) {
            clearInterval(raceAnimationInterval);
        }

        // 核心：使用 setInterval 播放动画
        raceAnimationInterval = setInterval(() => {
            if (turn >= log.length) {
                clearInterval(raceAnimationInterval);
                document.getElementById('status').innerText = state.result_message;
                document.getElementById('btn-new-race').disabled = false; // 允许新比赛
                return;
            }

            const turnPositions = log[turn];
            for (let i = 0; i < numHorses; i++) {
                const horseEl = document.getElementById(`horse-${i}`);
                // 按比例计算马匹在赛道上的百分比位置
                const progress = (turnPositions[i] / maxPos) * trackLength;
                horseEl.style.marginLeft = `${Math.min(progress, 100)}%`;
            }

            turn++;
        }, 200); // 200ms 播放一帧
    }
}

// =================================================
// 五子棋 专用的 UI 更新
// =================================================
function updateGomokuUI(state) {
    const statusEl = document.getElementById('status');
    const boardEl = document.getElementById('gomoku-board');

    statusEl.innerText = state.message;
    drawGomokuBoard(boardEl, state.board);

    if (state.status.endsWith('_win') || state.status === 'tie') {
        // 游戏结束，可以在这里禁用棋盘点击
        boardEl.style.pointerEvents = 'none';
    } else {
        boardEl.style.pointerEvents = 'auto';
    }
}

// 五子棋 绘制棋盘的辅助函数
function drawGomokuBoard(boardElement, boardData) {
    boardElement.innerHTML = ''; // 清空棋盘
    const boardSize = boardData.length;

    for (let y = 0; y < boardSize; y++) {
        for (let x = 0; x < boardSize; x++) {
            const cell = document.createElement('div');
            cell.className = 'gomoku-cell';
            cell.dataset.x = x;
            cell.dataset.y = y;

            const piece = boardData[y][x];
            if (piece !== 0) {
                const pieceDiv = document.createElement('div');
                pieceDiv.className = `gomoku-piece piece-${piece}`; // piece-1 或 piece-2
                cell.appendChild(pieceDiv);
            }

            boardElement.appendChild(cell);
        }
    }
}