from typing import Dict, List, Optional, Any
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QMessageBox,
)
from game.board import Board, PLAYER_1, PLAYER_2
from game.game import Game
from ai.minimax import MinimaxAgent
from ui.game_board import GameBoardWidget

MODE_HUMAN_VS_AI = "Human vs AI"
MODE_HUMAN_VS_HUMAN = "Human vs Human"
MODE_AI_VS_AI = "AI vs AI"


class AIWorker(QThread):
    move_computed = Signal(dict)

    def __init__(self, agent: Any, board_copy: Board, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.agent = agent
        self.board_copy = board_copy

    def run(self) -> None:
        self.move_computed.emit(self.agent.get_move(self.board_copy))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Connect Four AI")

        self.game = Game()
        self.ai_worker: Optional[AIWorker] = None
        self.ai_moves = 0
        self.ai_total_time = 0.0
        self.ai_total_pos = 0

        self._init_ui()
        self.start_new_game()

    def _init_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        left_layout = QVBoxLayout()
        self.lbl_status = QLabel("Хід: Гравець 1 (Червоні)")
        self.lbl_status.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_layout.addWidget(self.lbl_status)

        self.board_widget = GameBoardWidget()
        self.board_widget.column_clicked.connect(self.on_human_move)
        left_layout.addWidget(self.board_widget)
        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()

        grp_settings = QGroupBox("Налаштування")
        form_settings = QFormLayout(grp_settings)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems([MODE_HUMAN_VS_AI, MODE_HUMAN_VS_HUMAN, MODE_AI_VS_AI])
        self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
        form_settings.addRow("Режим:", self.combo_mode)

        self.lbl_depth_ai1 = QLabel("Глибина AI:")
        self.spin_depth_ai1 = QSpinBox()
        self.spin_depth_ai1.setRange(1, 8)
        self.spin_depth_ai1.setValue(5)
        form_settings.addRow(self.lbl_depth_ai1, self.spin_depth_ai1)

        self.lbl_depth_ai2 = QLabel("Глибина AI #1:")
        self.spin_depth_ai2 = QSpinBox()
        self.spin_depth_ai2.setRange(1, 8)
        self.spin_depth_ai2.setValue(4)
        form_settings.addRow(self.lbl_depth_ai2, self.spin_depth_ai2)

        self.btn_new = QPushButton("Нова гра")
        self.btn_new.clicked.connect(self.start_new_game)
        form_settings.addRow(self.btn_new)
        right_layout.addWidget(grp_settings)

        grp_ai_stat = QGroupBox("Останній хід AI")
        form_ai = QFormLayout(grp_ai_stat)
        self.lbl_stat_algo = QLabel("-")
        self.lbl_stat_depth = QLabel("-")
        self.lbl_stat_pos = QLabel("-")
        self.lbl_stat_time = QLabel("-")
        self.lbl_stat_col = QLabel("-")
        self.lbl_stat_eval = QLabel("-")
        form_ai.addRow("Алгоритм:", self.lbl_stat_algo)
        form_ai.addRow("Глибина:", self.lbl_stat_depth)
        form_ai.addRow("Позицій:", self.lbl_stat_pos)
        form_ai.addRow("Час:", self.lbl_stat_time)
        form_ai.addRow("Колонка:", self.lbl_stat_col)
        form_ai.addRow("Оцінка:", self.lbl_stat_eval)
        right_layout.addWidget(grp_ai_stat)

        grp_game_stat = QGroupBox("Статистика гри")
        form_game = QFormLayout(grp_game_stat)
        self.lbl_moves_count = QLabel("0")
        self.lbl_avg_time = QLabel("-")
        self.lbl_total_pos = QLabel("0")
        form_game.addRow("Всього ходів:", self.lbl_moves_count)
        form_game.addRow("Сер. час AI:", self.lbl_avg_time)
        form_game.addRow("Всього позицій AI:", self.lbl_total_pos)
        right_layout.addWidget(grp_game_stat)

        right_layout.addStretch()
        main_layout.addLayout(right_layout)

    def on_mode_changed(self) -> None:
        is_ai_vs_ai = (self.combo_mode.currentText() == MODE_AI_VS_AI)
        self.lbl_depth_ai1.setText("Глибина AI #2:" if is_ai_vs_ai else "Глибина AI:")
        self.lbl_depth_ai2.setVisible(is_ai_vs_ai)
        self.spin_depth_ai2.setVisible(is_ai_vs_ai)
        self.start_new_game()

    def start_new_game(self) -> None:
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker.wait()

        self.game.reset()
        self.board_widget.set_board(self.game.board)
        self.board_widget.set_winning_cells(None)

        self.ai_moves = 0
        self.ai_total_time = 0.0
        self.ai_total_pos = 0

        self.lbl_stat_algo.setText("-")
        self.lbl_stat_depth.setText("-")
        self.lbl_stat_pos.setText("-")
        self.lbl_stat_time.setText("-")
        self.lbl_stat_col.setText("-")
        self.lbl_stat_eval.setText("-")
        self.lbl_moves_count.setText("0")
        self.lbl_avg_time.setText("-")
        self.lbl_total_pos.setText("0")

        is_ai_vs_ai = (self.combo_mode.currentText() == MODE_AI_VS_AI)
        self.lbl_depth_ai2.setVisible(is_ai_vs_ai)
        self.spin_depth_ai2.setVisible(is_ai_vs_ai)

        self._update_status()
        self._check_and_trigger_ai()

    def _update_status(self) -> None:
        if self.game.is_over:
            return
        if self.game.current_player == PLAYER_1:
            self.lbl_status.setText("Хід: Гравець 1 (Червоні)")
        else:
            self.lbl_status.setText("Хід: Гравець 2 (Жовті)")

    def on_human_move(self, col: int) -> None:
        if self.game.is_over:
            return
        mode = self.combo_mode.currentText()
        if mode == MODE_HUMAN_VS_HUMAN or (mode == MODE_HUMAN_VS_AI and self.game.current_player == PLAYER_1):
            if self.game.make_move(col):
                self._handle_move_made()

    def _handle_move_made(self) -> None:
        self.board_widget.set_board(self.game.board)
        self.lbl_moves_count.setText(str(self.game.move_count))

        if self.game.is_over:
            if self.game.winner is not None:
                winner_name = "Гравець 1" if self.game.winner == PLAYER_1 else "Гравець 2"
                self.lbl_status.setText(f"Переміг: {winner_name}!")
                self.board_widget.set_winning_cells(self.game.board.get_winning_coordinates(self.game.winner))
                QMessageBox.information(self, "Кінець гри", f"Переміг {winner_name} за {self.game.move_count} ходів!")
            else:
                self.lbl_status.setText("Нічия!")
                QMessageBox.information(self, "Кінець гри", "Нічия! Усі клітинки заповнені.")
        else:
            self._update_status()
            self._check_and_trigger_ai()

    def _check_and_trigger_ai(self) -> None:
        if self.game.is_over:
            return

        mode = self.combo_mode.currentText()
        curr = self.game.current_player
        agent = None

        if mode == MODE_HUMAN_VS_AI and curr == PLAYER_2:
            agent = MinimaxAgent(depth=self.spin_depth_ai1.value(), piece=PLAYER_2)
        elif mode == MODE_AI_VS_AI:
            depth = self.spin_depth_ai2.value() if curr == PLAYER_1 else self.spin_depth_ai1.value()
            agent = MinimaxAgent(depth=depth, piece=curr)

        if agent:
            self.lbl_status.setText(self.lbl_status.text() + " (AI думає...)")
            delay = 300 if mode == MODE_AI_VS_AI else 50
            QTimer.singleShot(delay, lambda: self._start_ai(agent))

    def _start_ai(self, agent: MinimaxAgent) -> None:
        if not self.game.is_over:
            self.ai_worker = AIWorker(agent, self.game.get_board_copy(), self)
            self.ai_worker.move_computed.connect(self.on_ai_move_computed)
            self.ai_worker.start()

    def on_ai_move_computed(self, res: Dict[str, Any]) -> None:
        col = res.get("selected_column")
        if col is None:
            return

        self.lbl_stat_algo.setText(str(res.get("algorithm", "-")))
        self.lbl_stat_depth.setText(str(res.get("depth", "-")))
        self.lbl_stat_pos.setText(str(res.get("positions_analyzed", 0)))
        self.lbl_stat_time.setText(f"{res.get('move_time', 0.0):.2f} с")
        self.lbl_stat_col.setText(str(col))
        self.lbl_stat_eval.setText(str(res.get("evaluation", 0)))

        self.ai_moves += 1
        self.ai_total_time += res.get("move_time", 0.0)
        self.ai_total_pos += res.get("positions_analyzed", 0)

        self.lbl_avg_time.setText(f"{self.ai_total_time / self.ai_moves:.2f} с")
        self.lbl_total_pos.setText(str(self.ai_total_pos))

        if self.game.make_move(col):
            self._handle_move_made()
