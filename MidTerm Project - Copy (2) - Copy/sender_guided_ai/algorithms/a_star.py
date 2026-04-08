"""
A* search — uses Euclidean distance / scale as heuristic (admissible for this project’s maps).
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set, Tuple

from algorithms.heuristics import euclidean_heuristic
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


def a_star_search(
    graph: Graph,
    start: str,
    goal: str,
    blocked: Optional[Set[str]] = None,
) -> Tuple[Optional[List[str]], float, List[str]]:
    blocked = blocked or set()
    visited: Set[str] = set()
    if start in blocked or goal in blocked:
        return None, INF, []

    goal_node = graph.nodes[goal]

    def h(node_id: str) -> float:
        return euclidean_heuristic(graph.nodes[node_id], goal_node)

    # Priority: f = g + h
    pq: List[Tuple[float, float, int, str]] = []
    counter = 0
    g_start = 0.0
    f_start = g_start + h(start)
    heapq.heappush(pq, (f_start, g_start, counter, start))
    counter += 1

    g_score: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}

    while pq:
        _f, g_cost, _, current = heapq.heappop(pq)
        if g_cost > g_score.get(current, INF):
            continue
        visited.add(current)
        if current == goal:
            return _reconstruct_path(came_from, goal), g_cost, list(visited)

        for neighbor, weight in graph.get_neighbors(current):
            if neighbor in blocked:
                continue
            tentative = g_cost + weight
            if tentative < g_score.get(neighbor, INF):
                g_score[neighbor] = tentative
                came_from[neighbor] = current
                f = tentative + h(neighbor)
                heapq.heappush(pq, (f, tentative, counter, neighbor))
                counter += 1

    return None, INF, list(visited)
