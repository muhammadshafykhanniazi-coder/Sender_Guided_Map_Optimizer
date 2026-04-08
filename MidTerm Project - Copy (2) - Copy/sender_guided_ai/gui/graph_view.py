

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPen, QBrush, QPainter
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
)

from core.graph import Graph
from core.node import Node

NODE_R = 18
EDGE_Z = 0
EDGE_LABEL_Z = 0.5
NODE_Z = 2
NODE_LABEL_Z = 2.5
PATH_Z = 1
AGENT_Z = 5


class GraphMapView(QGraphicsView):
    """Interactive graph on a light “map”; emits node_clicked(node_id)."""

    node_clicked = pyqtSignal(str)

    # Map-like colors
    COL_EDGE = QColor("#dadce0")
    COL_NODE_FILL = QColor("#ffffff")
    COL_NODE_STROKE = QColor("#4285f4")
    COL_START = QColor("#34a853")
    COL_GOAL = QColor("#ea4335")
    COL_SENDER = QColor("#fbbc04")
    COL_BLOCKED = QColor("#5f6368")
    COL_AGENT = QColor("#9334e6")
    COL_EDGE_LABEL = QColor("#202124")      # dark gray for edge text
    COL_EDGE_LABEL_BG = QColor("#ffffff")   # white background behind edge label
    COL_VISITED = QColor("#b3e0ff")         # explored nodes (not start/goal/sender fill)
    COL_PATH_EDGE = QColor("#0f9d58")       # final shortest path on map
    COL_PATH_NODE = QColor("#c8e6c9")       # non-special nodes on the solution path
    COL_NODE_LABEL = QColor("#202124")


    def __init__(self, graph: Graph) -> None:
        super().__init__()
        self.graph = graph
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setBackgroundBrush(QBrush(QColor("#e8f0fe")))
        self.setDragMode(QGraphicsView.NoDrag)

        self._node_items: Dict[str, QGraphicsEllipseItem] = {}
        self._node_labels: Dict[str, QGraphicsTextItem] = {}
        self._edge_items: List[QGraphicsLineItem] = []
        self._edge_labels: List[QGraphicsTextItem] = []
        self._path_items: List[QGraphicsLineItem] = []
        self._agent: Optional[QGraphicsEllipseItem] = None

        self.start_id: Optional[str] = None
        self.goal_id: Optional[str] = None
        self.sender_id: Optional[str] = None

        self._path_nodes: List[str] = []
        self._path_node_set: Set[str] = set()
        self._visited_order: List[str] = []
        self._visited_shown: Set[str] = set()
        self._anim_step = 0
        self._max_anim_steps = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_animation)

        self._build_static()
        self.setSceneRect(self.scene.itemsBoundingRect().adjusted(-40, -40, 40, 40))

    # --- build ---
    def _pos(self, nid: str) -> Tuple[float, float]:
        n: Node = self.graph.nodes[nid]
        return float(n.x), float(n.y)

    def _build_static(self) -> None:
        drawn: Set[Tuple[str, str]] = set()
        pen_edge = QPen(self.COL_EDGE)
        pen_edge.setWidth(3)

        for src in self.graph.adjacency_list:
            x1, y1 = self._pos(src)
            for dst, w in self.graph.get_neighbors(src):
                key = tuple(sorted((src, dst)))
                if key in drawn:
                    continue
                drawn.add(key)
                x2, y2 = self._pos(dst)
                line = QGraphicsLineItem(x1, y1, x2, y2)
                line.setPen(pen_edge)
                line.setZValue(EDGE_Z)
                self.scene.addItem(line)
                self._edge_items.append(line)
                self._add_edge_cost_label(x1, y1, x2, y2, float(w))

        for nid in self.graph.nodes:
            x, y = self._pos(nid)
            el = QGraphicsEllipseItem(x - NODE_R, y - NODE_R, NODE_R * 2, NODE_R * 2)
            el.setBrush(QBrush(self.COL_NODE_FILL))
            el.setPen(QPen(self.COL_NODE_STROKE, 2))
            el.setZValue(NODE_Z)
            el.setData(0, nid)
            self.scene.addItem(el)
            self._node_items[nid] = el

            lab = QGraphicsTextItem(nid)
            lab.setDefaultTextColor(self.COL_NODE_LABEL)
            lab.setFont(QFont("Segoe UI", 11, QFont.Bold))
            br = lab.boundingRect()
            lab.setPos(x - br.width() * 0.5, y - br.height() * 0.5)
            lab.setZValue(NODE_LABEL_Z)
            lab.setData(0, nid)
            lab.setAcceptedMouseButtons(Qt.NoButton)
            self.scene.addItem(lab)
            self._node_labels[nid] = lab

        self._refresh_node_styles()

    def _fmt_weight(self, w: float) -> str:
        if abs(w - round(w)) < 1e-6:
            return str(int(round(w)))
        return f"{w:.1f}"

    def _add_edge_cost_label(self, x1: float, y1: float, x2: float, y2: float, w: float) -> None:
        """Draw edge weight at the segment midpoint (clicks pass through to nodes)."""
        mx = (x1 + x2) * 0.5
        my = (y1 + y2) * 0.5
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1.0
        ox = (-dy / length) * 14.0
        oy = (dx / length) * 14.0
        cx, cy = mx + ox, my + oy

        label = QGraphicsTextItem(self._fmt_weight(w))
        label.setDefaultTextColor(self.COL_EDGE_LABEL)
        label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        br = label.boundingRect()
        pad = 4.0
        lx = cx - br.width() * 0.5
        ly = cy - br.height() * 0.5
        label.setPos(lx, ly)
        label.setZValue(EDGE_LABEL_Z)

        bg = QGraphicsRectItem(lx - pad, ly - pad, br.width() + pad * 2.0, br.height() + pad * 2.0)
        bg.setPen(QPen(QColor("#dadce0")))
        bg.setBrush(QBrush(self.COL_EDGE_LABEL_BG))
        bg.setZValue(EDGE_LABEL_Z - 0.01)

        self.scene.addItem(bg)
        self.scene.addItem(label)
        self._edge_labels.append(label)

        for item in (label, bg):
            item.setAcceptedMouseButtons(Qt.NoButton)
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsFocusable, False)

    def _refresh_node_styles(self) -> None:
        for nid, el in self._node_items.items():
            if self.graph.is_blocked(nid):
                el.setBrush(QBrush(self.COL_BLOCKED))
                el.setPen(QPen(QColor("#202124"), 2))
                continue

            on_path = nid in self._path_node_set
            explored = nid in self._visited_shown

            if nid == self.start_id:
                el.setBrush(QBrush(self.COL_START))
                el.setPen(QPen(self.COL_PATH_EDGE if on_path else QColor("#1e8e3e"), 3 if on_path else 2))
            elif nid == self.goal_id:
                el.setBrush(QBrush(self.COL_GOAL))
                el.setPen(QPen(self.COL_PATH_EDGE if on_path else QColor("#c5221f"), 3 if on_path else 2))
            elif nid == self.sender_id:
                el.setBrush(QBrush(self.COL_SENDER))
                el.setPen(QPen(self.COL_PATH_EDGE if on_path else QColor("#e37400"), 3 if on_path else 2))
            elif on_path:
                el.setBrush(QBrush(self.COL_PATH_NODE))
                el.setPen(QPen(self.COL_PATH_EDGE, 3))
            elif explored:
                el.setBrush(QBrush(self.COL_VISITED))
                el.setPen(QPen(QColor("#1565c0"), 2))
            else:
                el.setBrush(QBrush(self.COL_NODE_FILL))
                el.setPen(QPen(self.COL_NODE_STROKE, 2))

    # --- interaction ---
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            nid = None
            if isinstance(item, QGraphicsEllipseItem):
                nid = item.data(0)
            elif isinstance(item, QGraphicsTextItem):
                nid = item.data(0)
            if isinstance(nid, str):
                self.node_clicked.emit(nid)
                event.accept()
                return
        super().mousePressEvent(event)

    def set_role(self, role: str, node_id: Optional[str]) -> None:
        """role is 'start' | 'goal' | 'sender' | 'clear'"""
        if role == "start":
            self.start_id = node_id
        elif role == "goal":
            self.goal_id = node_id
        elif role == "sender":
            self.sender_id = node_id
        self._refresh_node_styles()

    def toggle_blocked(self, node_id: str) -> None:
        # Cannot block special nodes
        if node_id in (self.start_id, self.goal_id, self.sender_id):
            return
        self.graph.toggle_blocked(node_id)
        self._refresh_node_styles()

    def clear_path_visuals(self) -> None:
        for it in self._path_items:
            self.scene.removeItem(it)
        self._path_items.clear()
        if self._agent is not None:
            self.scene.removeItem(self._agent)
            self._agent = None
        self._timer.stop()
        self._path_nodes = []
        self._path_node_set.clear()
        self._visited_order.clear()
        self._visited_shown.clear()
        self._anim_step = 0
        self._max_anim_steps = 0
        self._refresh_node_styles()

    @property
    def current_route(self) -> List[str]:
        """Last path prepared for drawing / animation (node ids in order)."""
        return list(self._path_nodes)

    def show_path(self, path: List[str]) -> None:
        """Draw path edges only; caller manages path_node_set / visited state."""
        for it in self._path_items:
            self.scene.removeItem(it)
        self._path_items.clear()
        if self._agent is not None:
            self.scene.removeItem(self._agent)
            self._agent = None
        self._timer.stop()
        self._path_nodes = []
        self._anim_step = 0
        self._max_anim_steps = 0
        if len(path) < 2:
            self._path_nodes = list(path)
            return
        pen = QPen(self.COL_PATH_EDGE)
        pen.setWidth(7)
        pen.setCapStyle(Qt.RoundCap)
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            x1, y1 = self._pos(a)
            x2, y2 = self._pos(b)
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(pen)
            line.setZValue(PATH_Z)
            self.scene.addItem(line)
            self._path_items.append(line)
        self._path_nodes = list(path)

    def display_route(self, path: List[str], visited_nodes: Optional[List[str]] = None) -> None:
        """Draw the route and place the agent at the start for step playback."""
        self.clear_path_visuals()
        self._visited_order = list(visited_nodes or [])
        self._path_node_set = set(path)
        self.show_path(path)
        self._refresh_node_styles()
        self.prepare_agent(path)

    def prepare_agent(self, path: List[str]) -> None:
        self._path_nodes = list(path)
        self._visited_shown.clear()
        self._anim_step = 0
        n_moves = max(0, len(path) - 1)
        self._max_anim_steps = max(len(self._visited_order), n_moves)
        if self._agent is not None:
            self.scene.removeItem(self._agent)
            self._agent = None
        if not path:
            return
        x, y = self._pos(path[0])
        self._agent = QGraphicsEllipseItem(x - 10, y - 10, 20, 20)
        self._agent.setBrush(QBrush(self.COL_AGENT))
        self._agent.setPen(QPen(QColor("#ffffff"), 2))
        self._agent.setZValue(AGENT_Z)
        self.scene.addItem(self._agent)

    def start_step_animation(self, interval_ms: int = 420) -> None:
        if not self._visited_order and len(self._path_nodes) < 2:
            return
        self._visited_shown.clear()
        self._anim_step = 0
        n_moves = max(0, len(self._path_nodes) - 1)
        self._max_anim_steps = max(len(self._visited_order), n_moves)
        if self._max_anim_steps == 0:
            return
        self._timer.start(interval_ms)

    def stop_animation(self) -> None:
        self._timer.stop()

    def _tick_animation(self) -> None:
        if self._anim_step >= self._max_anim_steps:
            self._timer.stop()
            return

        if self._anim_step < len(self._visited_order):
            vn = self._visited_order[self._anim_step]
            self._visited_shown.add(vn)
            self._refresh_node_styles()

        if self._agent is not None and self._path_nodes:
            n_moves = len(self._path_nodes) - 1
            if self._anim_step < n_moves:
                nid = self._path_nodes[self._anim_step + 1]
                x, y = self._pos(nid)
                self._agent.setRect(x - 10, y - 10, 20, 20)

        self._anim_step += 1
        if self._anim_step >= self._max_anim_steps:
            self._timer.stop()

    def reset_all(self) -> None:
        self.stop_animation()
        self.clear_path_visuals()
        self.start_id = None
        self.goal_id = None
        self.sender_id = None
        for nid in list(self.graph.blocked):
            self.graph.set_blocked(nid, False)
        self._refresh_node_styles()
