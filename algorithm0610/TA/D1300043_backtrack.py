import sys


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    N = int(data[pos]); pos += 1
    T = int(data[pos]); pos += 1
    p = [0] * N
    s = [0] * N
    for i in range(N):
        p[i] = int(data[pos]); pos += 1
        s[i] = int(data[pos]); pos += 1
    rows = [None] * N
    for i in range(N):
        base = pos + i * N
        rows[i] = [int(x) for x in data[base:base + N]]
    pos += N * N
    del data

    back = [rows[i][0] for i in range(N)]

    min_in = [None] * N
    foot = [0] * N
    for j in range(1, N):
        m = None
        for i in range(N):
            if i != j:
                c = rows[i][j]
                if c != 0 and (m is None or c < m):
                    m = c
        min_in[j] = m
        foot[j] = (m + s[j]) if m is not None else None
    min_back = min((back[j] for j in range(1, N) if back[j] != 0), default=0)

    order = sorted((j for j in range(1, N) if foot[j] is not None), key=lambda j: -p[j])

    best = [0]
    best_path = [[0, 0]]
    v0 = bytearray(N); v0[0] = 1
    cur = 0; tu = 0; rew = 0; route = [0]
    while True:
        row = rows[cur]; bj = -1; bp = 0; bc = 1; rem = T - tu
        for j in range(1, N):
            if v0[j]:
                continue
            c = row[j]
            if c == 0:
                continue
            bk = back[j]
            if bk == 0:
                continue
            cost = c + s[j]
            if cost + bk > rem:
                continue
            if bj == -1 or p[j] * bc > bp * cost:
                bj = j; bp = p[j]; bc = cost
        if bj == -1:
            break
        tu += row[bj] + s[bj]; rew += p[bj]; v0[bj] = 1; route.append(bj); cur = bj
    if rew > best[0]:
        best[0] = rew; best_path[0] = route + [0]

    visited = bytearray(N); visited[0] = 1
    path = [0]
    memo = {}                    

    def bound(time_used):
        cap = T - time_used - min_back
        if cap < 0:
            return 0
        b = 0
        for j in order:
            if visited[j]:
                continue
            f = foot[j]
            if f <= cap:
                b += p[j]; cap -= f
            else:
                b += p[j] * cap // f
                break
        return b

    def dfs(cur, mask, time_used, reward):
        bc = back[cur]
        if cur != 0 and bc != 0 and time_used + bc <= T and reward > best[0]:
            best[0] = reward
            best_path[0] = path + [0]
        if reward + bound(time_used) <= best[0]:
            return
        row = rows[cur]
        for j in order:
            if mask >> j & 1:
                continue
            c = row[j]
            if c == 0:
                continue
            nt = time_used + c + s[j]
            if nt > T:
                continue
            nmask = mask | (1 << j)
            key = (nmask, j)
            prev = memo.get(key)
            if prev is not None and prev <= nt:   
                continue
            memo[key] = nt
            path.append(j)
            dfs(j, nmask, nt, reward + p[j])
            path.pop()

    dfs(0, 1, 0, 0)

    out = sys.stdout
    out.write(str(best[0])); out.write("\n")
    out.write(" ".join(map(str, best_path[0]))); out.write("\n")


main()
