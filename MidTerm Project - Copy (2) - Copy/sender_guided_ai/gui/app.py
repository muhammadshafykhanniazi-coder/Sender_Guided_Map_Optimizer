import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QScrollArea, QWidget

from core.default_map import build_default_graph
from core.path_manager import PathManager
from gui.graph_view import GraphMapView
from gui.sidebar import Sidebar


def apply_style(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(
        """
        QMainWindow { background: #ffffff; }
        QWidget { color: #202124; font-size: 14px; }
        QLabel#titleLabel { font-size: 20px; font-weight: 700; color: #1a73e8; }
        QLabel#subtitleLabel { color: #5f6368; font-size: 13px; }
        QLabel#tipLabel { color: #80868b; font-size: 12px; }
        QGroupBox {
            font-weight: 600;
            border: 1px solid #dadce0;
            border-radius: 10px;
            margin-top: 10px;
            padding: 12px 10px 10px 10px;
            background: #fafafa;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
        QPushButton {
            background: #1a73e8;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            padding: 8px 12px;
        }
        QPushButton:hover { background: #1967d2; }
        QPushButton:pressed { background: #185abc; }
        QComboBox {
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 8px 10px;
            background: white;
        }
        QRadioButton { spacing: 8px; }
        QScrollArea { border: none; background: #e8eaed; }
        """
    )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sender-Guided Pathfinding — UCS & A*")
        self.resize(1180, 720)

        graph = build_default_graph()
        self.view = GraphMapView(graph)
        manager = PathManager(graph, algorithm="ucs")
        self.panel = Sidebar(self.view, manager)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.view)

        central = QWidget()
        lay = QHBoxLayout()
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(16)
        lay.addWidget(scroll, stretch=3)
        lay.addWidget(self.panel, stretch=1)
        central.setLayout(lay)
        self.setCentralWidget(central)


def main() -> None:
    app = QApplication(sys.argv)
    apply_style(app)
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
