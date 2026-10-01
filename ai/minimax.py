import math
import time
from typing import Dict, List, Optional, Tuple, Any
from game.board import Board, PLAYER_1, PLAYER_2
from ai.evaluation import evaluate_board

COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6]


class MinimaxAgent:
    def __init__(self, depth: int = 6, piece: int = PLAYER_2) -> None:
        self.depth: int = depth
        self.piece: int = piece
        self.opponent_piece: int = PLAYER_1 if piece == PLAYER_2 else PLAYER_2
        self.positions_analyzed: int = 0

    def _get_moves(self, board: Board) -> List[int]:
        valid = set(board.get_valid_locations())
        return [c for c in COLUMN_ORDER if c in valid]

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, is_max: bool) -> Tuple[Optional[int], int]:
        self.positions_analyzed += 1
        moves = self._get_moves(board)

        if board.check_win(self.piece):
            return None, 100_000 + depth
        if board.check_win(self.opponent_piece):
            return None, -100_000 - depth
        if not moves:
            return None, 0
        if depth == 0:
            return None, evaluate_board(board, self.piece)

        best_col = moves[0]
        if is_max:
            val = -math.inf
            for col in moves:
                row = board.get_next_open_row(col)
                board.drop_piece(row, col, self.piece)
                _, score = self._minimax(board, depth - 1, alpha, beta, False)
                board.undo_move(row, col)
                if score > val:
                    val, best_col = score, col
                alpha = max(alpha, val)
                if alpha >= beta:
                    break
            return best_col, int(val)
        else:
            val = math.inf
            for col in moves:
                row = board.get_next_open_row(col)
                board.drop_piece(row, col, self.opponent_piece)
                _, score = self._minimax(board, depth - 1, alpha, beta, True)
                board.undo_move(row, col)
                if score < val:
                    val, best_col = score, col
                beta = min(beta, val)
                if alpha >= beta:
                    break
            return best_col, int(val)

    def get_move(self, board: Board) -> Dict[str, Any]:
        moves = self._get_moves(board)
        if not moves:
            return {"algorithm": "Minimax", "depth": self.depth, "positions_analyzed": 0, "move_time": 0.0, "selected_column": None, "evaluation": 0}

        self.positions_analyzed = 0
        start = time.perf_counter()
        best_col, eval_val = self._minimax(board, self.depth, -math.inf, math.inf, True)
        elapsed = round(time.perf_counter() - start, 3)

        return {
            "algorithm": "Minimax",
            "depth": self.depth,
            "positions_analyzed": self.positions_analyzed,
            "move_time": elapsed,
            "selected_column": best_col if best_col is not None else moves[0],
            "evaluation": eval_val,
        }
