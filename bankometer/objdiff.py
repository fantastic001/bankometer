

from enum import Enum
from os import remove


class ChangeType(Enum):
    ADD = 1
    REMOVE = 2
    UPDATE = 3
    RECURSIVE_CHANGE = 4

    def __str__(self):
        return self.name.lower()

class Change:
    def __init__(self, change_type, path, old_value, value):
        self.change_type = change_type
        self.path = path
        self.old_value = old_value
        self.value = value

    def __str__(self):
        if self.change_type == ChangeType.REMOVE:
            return f"{self.change_type} at {self.path}: {self.old_value} removed"
        return f"{self.change_type} at {self.path}: {self.value}"

    def __repr__(self):
        return str(self)

def diff(a, b):
    if type(a) != type(b):
        raise TypeError(f"Cannot compare different types: {type(a)} vs {type(b)}")
    if isinstance(a, dict):
        changes = []
        for key in set(a.keys()).union(b.keys()):
            if key not in a:
                changes.append(Change(ChangeType.ADD, key, None, b[key]))
            elif key not in b:
                changes.append(Change(ChangeType.REMOVE, key, a[key], None))
            else:
                if a[key] != b[key]:
                    if any(isinstance(a[key], t) for t in (dict, list)) and any(isinstance(b[key], t) for t in (dict, list)):
                        changes.append(Change(ChangeType.RECURSIVE_CHANGE, key, a[key], diff(a[key], b[key])))
                    else:
                        changes.append(Change(ChangeType.UPDATE, key, a[key], b[key]))
        return changes
    elif isinstance(a, list):
        m = len(a)
        n = len(b)
        cost = [[0 for _ in range(n+1)] for _ in range(m+1)]
        parent = {x: {y: None for y in range(n+1)} for x in range(m+1)}
        for i in range(m+1):
            for j in range(n+1):
                if i == 0 and j == 0:
                    cost[i][j] = 0
                elif i == 0:
                    cost[i][j] = j
                    parent[i][j] = (i, j-1)
                elif j == 0:
                    cost[i][j] = i
                    parent[i][j] = (i-1, j)
                else:
                    if a[i-1] == b[j-1]:
                        cost[i][j] = cost[i-1][j-1]
                        parent[i][j] = (i-1, j-1)
                    else:
                        if cost[i-1][j] + 1 < cost[i][j-1] + 1:
                            cost[i][j] = cost[i-1][j] + 1
                            parent[i][j] = (i-1, j)
                        else:
                            cost[i][j] = cost[i][j-1] + 1
                            parent[i][j] = (i, j-1)
        changes = [] 
        i, j = m, n
        while parent[i][j] is not None:
            if parent[i][j] == (i-1, j):
                changes.append(Change(ChangeType.REMOVE, i-1, a[i-1], None))
                i -= 1
            elif parent[i][j] == (i, j-1):
                changes.append(Change(ChangeType.ADD, j-1, None, b[j-1]))
                j -= 1
            else:
                i -= 1
                j -= 1
        changes.reverse()
        return changes
    else:
        if a != b:
            return [Change(ChangeType.UPDATE, '', a, b)]
        else:
            return []

if __name__ == "__main__":
    a = {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': [4, 5]}
    b = {'a': 1, 'b': {'c': 2, 'd': 4}, 'f': [6, 7]}

    changes = diff(a, b)
    for change in changes:
        print(change)
    print()
    for change in diff([2, 3, 4], [3, 4, 5]):
        print(change)