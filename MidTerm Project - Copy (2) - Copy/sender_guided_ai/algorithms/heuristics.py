
#Heuristic helpers for A*. Scale keeps h small vs typical integer edge weights.


from __future__ import annotations

import math


def euclidean_heuristic(a, b) -> float:
    #Straight-line distance between node positions (lower bound on travel cost
    dx = a.x - b.x
    dy = a.y - b.y
    return math.hypot(dx, dy) / 120.0
