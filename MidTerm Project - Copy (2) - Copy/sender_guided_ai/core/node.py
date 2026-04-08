class Node:
    def __init__(self, node_id, x, y):
        self.id = node_id
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Node({self.id})"
