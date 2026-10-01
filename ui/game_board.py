from typing import List, Optional, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPaintEvent, QMouseEvent
from PySide6.QtWidgets import QWidget
from game.board import Board, ROWS, COLS, EMPTY, PLAYER_1, PLAYER_2


class GameBoardWidget(QWidget):
    column_clicked = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.board: Optional[Board] = None
        self.winning_cells: Optional[List[Tuple[int, int]]] = None
        self.setFixedSize(490, 420)

    def set_board(self, board: Board) -> None:
        self.board = board
        self.update()

    def set_winning_cells(self, cells: Optional[List[Tuple[int, int]]]) -> None:
        self.winning_cells = cells
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.board:
            col = int(event.position().x() // 70)
            if 0 <= col < COLS and self.board.is_valid_location(col):
                self.column_clicked.emit(col)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(0, 102, 204))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())

        for r in range(ROWS):
            for c in range(COLS):
                x = c * 70 + 10
                y = (ROWS - 1 - r) * 70 + 10

                val = self.board.grid[r][c] if self.board else EMPTY
                if val == PLAYER_1:
                    painter.setBrush(QColor(220, 40, 40))
                elif val == PLAYER_2:
                    painter.setBrush(QColor(240, 200, 20))
                else:
                    painter.setBrush(QColor(240, 240, 240))

                if self.winning_cells and (r, c) in self.winning_cells:
                    painter.setPen(QPen(QColor(0, 220, 0), 4))
                else:
                    painter.setPen(QPen(QColor(0, 0, 0), 1))

                painter.drawEllipse(x, y, 50, 50)
