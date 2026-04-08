"""
Sender-guided routing: shortest path Start → Sender → Goal using one search backend.
"""

from __future__ import annotations

from typing import List, Optional, Set, Tuple

from algorithms.a_star import a_star_search
from algorithms.ucs import uniform_cost_search
from core.graph import Graph


class PathManager:
    """Pick UCS or A*, then run two legs: start→sender and sender→goal."""

    def __init__(self, graph: Graph, algorithm: str = "ucs") -> None:
        self.graph = graph
        self.algorithm = algorithm

    def set_algorithm(self, algorithm: str) -> None:
        self.algorithm = algorithm.lower().strip()

    def _search(self, start: str, goal: str):
        blocked = self.graph.blocked
        if self.algorithm == "astar":
            return a_star_search(self.graph, start, goal, blocked)
        return uniform_cost_search(self.graph, start, goal, blocked)

    def find_path(self, start: str, sender: str, goal: str) -> Tuple[Optional[List[str]], float, List[str]]:
        """Full route through the sender waypoint (sender acts as the guide checkpoint)."""
        path1, cost1, vis1 = self._search(start, sender)
        if path1 is None:
            return None, float("inf"), []

        path2, cost2, vis2 = self._search(sender, goal)
        if path2 is None:
            return None, float("inf"), []

        merged = path1 + path2[1:]
        vis2_tail = vis2[1:] if vis2 and vis2[0] == sender else vis2
        seen: Set[str] = set()
        merged_vis: List[str] = []
        for nid in vis1 + vis2_tail:
            if nid not in seen:
                seen.add(nid)
                merged_vis.append(nid)
        return merged, cost1 + cost2, merged_vis
