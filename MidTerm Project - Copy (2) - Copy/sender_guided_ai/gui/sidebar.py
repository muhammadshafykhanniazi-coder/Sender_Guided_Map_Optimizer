"""
Simple side panel: algorithm, click mode, run / play / reset, optional stats.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core.path_manager import PathManager
from gui.graph_view import GraphMapView


class Sidebar(QWidget):
    def __init__(self, view: GraphMapView, manager: PathManager) -> None:
        super().__init__()
        self.view = view
        self.manager = manager

        layout = QVBoxLayout()
        layout.setSpacing(12)

        t = QLabel("Pathfinding Map")
        t.setObjectName("titleLabel")
        layout.addWidget(t)

        sub = QLabel("Choose Start, Sender, and Goal on the map, then Run.")
        sub.setWordWrap(True)
        sub.setObjectName("subtitleLabel")
        layout.addWidget(sub)

        algo = QGroupBox("Algorithm")
        al = QVBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems(["UCS (Uniform Cost)", "A* (heuristic)"])
        self.combo.currentIndexChanged.connect(self._on_algo_change)
        al.addWidget(self.combo)
        algo.setLayout(al)
        layout.addWidget(algo)

        mode = QGroupBox("Click mode")
        ml = QVBoxLayout()
        self.r_start = QRadioButton("Set Start (green)")
        self.r_sender = QRadioButton("Set Sender (yellow)")
        self.r_goal = QRadioButton("Set Goal (red)")
        self.r_obs = QRadioButton("Toggle obstacle (gray)")
        self.r_start.setChecked(True)
        for r in (self.r_start, self.r_sender, self.r_goal, self.r_obs):
            ml.addWidget(r)
        mode.setLayout(ml)
        layout.addWidget(mode)

        row = QHBoxLayout()
        self.btn_run = QPushButton("Run")
        self.btn_play = QPushButton("Play steps")
        self.btn_reset = QPushButton("Reset")
        for b in (self.btn_run, self.btn_play, self.btn_reset):
            b.setMinimumHeight(44)
            b.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.btn_run)
        row.addWidget(self.btn_play)
        layout.addLayout(row)
        layout.addWidget(self.btn_reset)

        stats = QGroupBox("Route info")
        sl = QVBoxLayout()
        self.lbl_cost = QLabel("Total cost: —")
        self.lbl_steps = QLabel("Steps (edges): —")
        self.lbl_traversed = QLabel("Nodes traversed: —")
        for lab in (self.lbl_cost, self.lbl_steps, self.lbl_traversed):
            lab.setTextInteractionFlags(Qt.TextSelectableByMouse)
            sl.addWidget(lab)
        stats.setLayout(sl)
        layout.addWidget(stats)

        tip = QLabel("Sender-guided route = Start → Sender → Goal (two shortest legs).")
        tip.setWordWrap(True)
        tip.setObjectName("tipLabel")
        layout.addWidget(tip)

        layout.addStretch(1)
        self.setLayout(layout)

        self.view.node_clicked.connect(self._on_node)
        self.btn_run.clicked.connect(self.run_path)
        self.btn_play.clicked.connect(self.play_animation)
        self.btn_reset.clicked.connect(self.reset)

        self._on_algo_change()

    def _on_algo_change(self) -> None:
        name = "astar" if self.combo.currentIndex() == 1 else "ucs"
        self.manager.set_algorithm(name)

    def _mode(self) -> str:
        if self.r_start.isChecked():
            return "start"
        if self.r_sender.isChecked():
            return "sender"
        if self.r_goal.isChecked():
            return "goal"
        return "obstacle"

    def _on_node(self, node_id: str) -> None:
        m = self._mode()
        if m == "obstacle":
            self.view.toggle_blocked(node_id)
            return
        if self.view.graph.is_blocked(node_id):
            QMessageBox.information(self, "Blocked", "Clear the obstacle on this node first.")
            return
        self.view.set_role(m, node_id)

    def run_path(self) -> None:
        s, g, z = self.view.start_id, self.view.goal_id, self.view.sender_id
        if not s or not g or not z:
            QMessageBox.information(self, "Missing points", "Please set Start, Sender, and Goal.")
            return
        if len({s, g, z}) < 3:
            QMessageBox.warning(self, "Distinct nodes", "Start, Sender, and Goal must be three different places.")
            return

        path, cost, visited_nodes = self.manager.find_path(s, z, g)
        self.view.stop_animation()

        if path is None:
            self.view.clear_path_visuals()
            QMessageBox.warning(self, "No path", "No route exists with the current obstacles.")
            self.lbl_cost.setText("Total cost: —")
            self.lbl_steps.setText("Steps (edges): —")
            self.lbl_traversed.setText("Nodes traversed: —")
            return

        self.view.display_route(path, visited_nodes)
        self.lbl_cost.setText(f"Total cost: {cost:.2f}")
        self.lbl_steps.setText(f"Steps (edges): {max(0, len(path) - 1)}")
        self.lbl_traversed.setText(f"Nodes traversed: {len(visited_nodes)}")

    def play_animation(self) -> None:
        if not self.view.current_route:
            self.run_path()
        route = self.view.current_route
        if route:
            self.view.prepare_agent(route)
            self.view.start_step_animation()

    def reset(self) -> None:
        self.view.reset_all()
        self.lbl_cost.setText("Total cost: —")
        self.lbl_steps.setText("Steps (edges): —")
        self.lbl_traversed.setText("Nodes traversed: —")
