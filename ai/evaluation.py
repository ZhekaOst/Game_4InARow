from typing import List
from game.board import Board, EMPTY, PLAYER_1, PLAYER_2, DIRECTIONS


def evaluate_window(window: List[int], piece: int, opponent: int) -> int:
    p_cnt = window.count(piece)
    o_cnt = window.count(opponent)
    empty = window.count(EMPTY)

    if p_cnt == 4:
        return 100_000
    if p_cnt == 3 and empty == 1:
        return 100
    if p_cnt == 2 and empty == 2:
        return 10
    if o_cnt == 3 and empty == 1:
        return -120
    if o_cnt == 2 and empty == 2:
        return -10
    return 0


def evaluate_board(board: Board, piece: int) -> int:
    opponent = PLAYER_1 if piece == PLAYER_2 else PLAYER_2
    score = 0

    center = [board.grid[r][board.cols // 2] for r in range(board.rows)]
    score += (center.count(piece) - center.count(opponent)) * 3

    for r in range(board.rows):
        for c in range(board.cols):
            for dr, dc in DIRECTIONS:
                if 0 <= r + 3 * dr < board.rows and 0 <= c + 3 * dc < board.cols:
                    window = [board.grid[r + i * dr][c + i * dc] for i in range(4)]
                    score += evaluate_window(window, piece, opponent)

    return score
