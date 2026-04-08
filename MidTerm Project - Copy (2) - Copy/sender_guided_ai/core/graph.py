"""
Weighted directed graph for pathfinding. Neighbors are (node_id, edge_weight).

Blocked nodes cannot be entered (used as obstacles). Keep the graph simple:
add nodes, add edges, mark blocked for the UI.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

Neighbor = Tuple[str, float]


class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[str, object] = {}
        self.adjacency_list: Dict[str, List[Neighbor]] = {}
        self.blocked: Set[str] = set()

    def add_node(self, node) -> None:
        self.nodes[node.id] = node
        self.adjacency_list[node.id] = []

    def add_edge(self, source: str, destination: str, weight: float) -> None:
        if source not in self.nodes or destination not in self.nodes:
            raise ValueError("Both endpoints must exist before adding an edge.")
        self.adjacency_list[source].append((destination, weight))

    def add_undirected_edge(self, a: str, b: str, weight: float) -> None:
        """Two-way street with the same cost (typical for map-like links)."""
        self.add_edge(a, b, weight)
        self.add_edge(b, a, weight)

    def get_neighbors(self, node_id: str) -> List[Neighbor]:
        return self.adjacency_list.get(node_id, [])

    def is_blocked(self, node_id: str) -> bool:
        return node_id in self.blocked

    def set_blocked(self, node_id: str, blocked: bool) -> None:
        if node_id not in self.nodes:
            return
        if blocked:
            self.blocked.add(node_id)
        else:
            self.blocked.discard(node_id)

    def toggle_blocked(self, node_id: str) -> None:
        self.set_blocked(node_id, not self.is_blocked(node_id))
