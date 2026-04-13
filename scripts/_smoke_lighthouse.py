from collections import deque


def energized(grid, start):
    R, C = len(grid), len(grid[0])
    visited = set()
    q = deque([start])
    while q:
        r, c, dr, dc = q.popleft()
        if not (0 <= r < R and 0 <= c < C):
            continue
        if (r, c, dr, dc) in visited:
            continue
        visited.add((r, c, dr, dc))
        ch = grid[r][c]
        if ch == '.':
            nxts = [(dr, dc)]
        elif ch == '/':
            nxts = [(-dc, -dr)]
        elif ch == '\\':
            nxts = [(dc, dr)]
        elif ch == '|':
            nxts = [(-1, 0), (1, 0)] if dr == 0 else [(dr, dc)]
        elif ch == '-':
            nxts = [(0, -1), (0, 1)] if dc == 0 else [(dr, dc)]
        else:
            nxts = []
        for ndr, ndc in nxts:
            q.append((r + ndr, c + ndc, ndr, ndc))
    return len({(r, c) for (r, c, _, _) in visited})


g1 = ['....', '....', '....']
assert energized(g1, (0, 0, 0, 1)) == 4, energized(g1, (0, 0, 0, 1))

g2 = ['..', './']
assert energized(g2, (1, 0, 0, 1)) == 3, energized(g2, (1, 0, 0, 1))

g3 = ['...', '.|.', '...']
assert energized(g3, (1, 0, 0, 1)) == 4, energized(g3, (1, 0, 0, 1))

print("OK all 3 smoke tests passed")
