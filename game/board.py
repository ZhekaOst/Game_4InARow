from typing import List, Optional, Tuple

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (-1, 1)]


class Board:
    def __init__(self) -> None:
        self.rows: int = ROWS
        self.cols: int = COLS
        self.grid: List[List[int]] = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

    def reset(self) -> None:
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

    def is_valid_location(self, col: int) -> bool:
        return 0 <= col < self.cols and self.grid[self.rows - 1][col] == EMPTY

    def get_valid_locations(self) -> List[int]:
        return [c for c in range(self.cols) if self.is_valid_location(c)]

    def get_next_open_row(self, col: int) -> Optional[int]:
        if 0 <= col < self.cols:
            for r in range(self.rows):
                if self.grid[r][col] == EMPTY:
                    return r
        return None

    def drop_piece(self, row: int, col: int, piece: int) -> None:
        self.grid[row][col] = piece

    def undo_move(self, row: int, col: int) -> None:
        self.grid[row][col] = EMPTY

    def get_winning_coordinates(self, piece: int) -> Optional[List[Tuple[int, int]]]:
        for r in range(self.rows):
            for c in range(self.cols):
                for dr, dc in DIRECTIONS:
                    if 0 <= r + 3 * dr < self.rows and 0 <= c + 3 * dc < self.cols:
                        if all(self.grid[r + i * dr][c + i * dc] == piece for i in range(4)):
                            return [(r + i * dr, c + i * dc) for i in range(4)]
        return None

    def check_win(self, piece: int) -> bool:
        return self.get_winning_coordinates(piece) is not None

    def is_full(self) -> bool:
        return len(self.get_valid_locations()) == 0

    def is_draw(self) -> bool:
        return self.is_full() and not self.check_win(PLAYER_1) and not self.check_win(PLAYER_2)

    def copy(self) -> "Board":
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        return new_board
