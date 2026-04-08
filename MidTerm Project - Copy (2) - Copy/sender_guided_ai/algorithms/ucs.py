"""
Uniform Cost Search — optimal path on non-negative weighted edges.
Uses a parent map + g-scores (no full path stored in the priority queue).
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set, Tuple

from core.graph import Graph

INF = float("inf")


def _reconstruct_path(came_from: Dict[str, Optional[str]], goal: str) -> List[str]:
    out: List[str] = []
    cur: Optional[str] = goal
    while cur is not None:
        out.append(cur)
        cur = came_from.get(cur)
    out.reverse()
    return out


def uniform_cost_search(
    graph: Graph,
    start: str,
    goal: str,
    blocked: Optional[Set[str]] = None,
) -> Tuple[Optional[List[str]], float, List[str]]:
    blocked = blocked or set()
    visited: Set[str] = set()
    if start in blocked or goal in blocked:
        return None, INF, []

    pq: List[Tuple[float, int, str]] = []
    counter = 0
    heapq.heappush(pq, (0.0, counter, start))
    counter += 1

    g_score: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}

    while pq:
        cost, _, current = heapq.heappop(pq)
        if cost > g_score.get(current, INF):
            continue
        visited.add(current)
        if current == goal:
            return _reconstruct_path(came_from, goal), cost, list(visited)

        for neighbor, weight in graph.get_neighbors(current):
            if neighbor in blocked:
                continue
            new_cost = cost + weight
            if new_cost < g_score.get(neighbor, INF):
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(pq, (new_cost, counter, neighbor))
                counter += 1

    return None, INF, list(visited)
