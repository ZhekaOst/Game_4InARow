from typing import Optional, Tuple
from game.board import Board, PLAYER_1, PLAYER_2


class Game:
    def __init__(self) -> None:
        self.board: Board = Board()
        self.current_player: int = PLAYER_1
        self.winner: Optional[int] = None
        self.is_over: bool = False
        self.move_count: int = 0
        self.last_move: Optional[Tuple[int, int]] = None

    def reset(self) -> None:
        self.board.reset()
        self.current_player = PLAYER_1
        self.winner = None
        self.is_over = False
        self.move_count = 0
        self.last_move = None

    def switch_player(self) -> None:
        self.current_player = PLAYER_2 if self.current_player == PLAYER_1 else PLAYER_1

    def make_move(self, col: int) -> bool:
        if self.is_over or not self.board.is_valid_location(col):
            return False

        row = self.board.get_next_open_row(col)
        if row is None:
            return False

        self.board.drop_piece(row, col, self.current_player)
        self.last_move = (row, col)
        self.move_count += 1

        if self.board.check_win(self.current_player):
            self.winner = self.current_player
            self.is_over = True
            return True

        if self.board.is_full():
            self.winner = None
            self.is_over = True
            return True

        self.switch_player()
        return True

    def get_board_copy(self) -> Board:
        return self.board.copy()
