"""
Weighted “city” graph: node pixel positions for drawing and A* heuristics.
Larger map (16 nodes) with varied road costs.
"""

from __future__ import annotations

from core.graph import Graph
from core.node import Node


def build_default_graph() -> Graph:
    g = Graph()

    # Three staggered rows + shortcuts — fits a wide scrollable view
    layout = {
        "A": (60, 65),
        "B": (200, 55),
        "C": (340, 70),
        "D": (480, 58),
        "E": (620, 72),
        "F": (760, 62),
        "G": (130, 195),
        "H": (270, 188),
        "I": (410, 200),
        "J": (550, 192),
        "K": (690, 205),
        "L": (220, 325),
        "M": (360, 318),
        "N": (500, 328),
        "O": (640, 320),
        "P": (780, 335),
    }

    for nid, (x, y) in layout.items():
        g.add_node(Node(nid, x, y))

    # Each tuple is one undirected road (cost shown on the map)
    roads = [
        # Top backbone
        ("A", "B", 4),
        ("B", "C", 3),
        ("C", "D", 4),
        ("D", "E", 3),
        ("E", "F", 5),
        # Top ↔ middle
        ("A", "G", 6),
        ("B", "H", 4),
        ("C", "I", 3),
        ("D", "J", 4),
        ("E", "K", 4),
        ("F", "K", 5),
        # Middle ring
        ("G", "H", 2),
        ("H", "I", 3),
        ("I", "J", 3),
        ("J", "K", 4),
        # Middle ↔ bottom
        ("G", "L", 5),
        ("H", "M", 3),
        ("I", "N", 2),
        ("J", "O", 4),
        ("K", "P", 5),
        # Bottom chain
        ("L", "M", 4),
        ("M", "N", 3),
        ("N", "O", 4),
        ("O", "P", 3),
        # Useful shortcuts / cross-links
        ("H", "L", 6),
        ("I", "M", 4),
        ("J", "N", 3),
        ("C", "H", 5),
        ("D", "I", 4),
        ("M", "J", 5),
        ("N", "K", 5),
        ("L", "I", 7),
        ("G", "M", 6),
    ]

    for a, b, w in roads:
        g.add_undirected_edge(a, b, float(w))

    return g
