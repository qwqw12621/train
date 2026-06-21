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
    bit = [1 << j for j in range(N)]
    foot = [1 << 62] * N
    for j in range(1, N):
        m = None
        for i in range(N):
            if i != j:
                c = rows[i][j]
                if c != 0 and (m is None or c < m):
                    m = c
        if m is not None:
            foot[j] = m + s[j]
    min_back = min((back[j] for j in range(1, N) if back[j] != 0), default=0)
    order = sorted(range(1, N), key=lambda j: -p[j]); M = len(order)
    of = [foot[j] for j in order]
    op = [p[j] for j in order]
    # 子節點依「獎勵/成本」由高到低排序：DFS 先走較佳分支，incumbent 早早變強 → 剪枝更有效
    adj = []
    for i in range(N):
        lst = [(j, rows[i][j], s[j], p[j], bit[j]) for j in range(1, N) if i != j and rows[i][j] != 0]
        lst.sort(key=lambda e: e[3] * 1000 // (e[1] + e[2] + 1))
        adj.append(lst)  # 升冪：用 stack(LIFO) pop 時最佳者最後入最先出

    def reward(route):
        return sum(p[x] for x in route if x != 0)

    # ---------- incumbent 下界：多起點比值貪婪 ----------
    def greedy_from(first):
        vis = bytearray(N); vis[0] = 1; cur = 0; tu = 0; route = [0]
        if first is not None:
            c = rows[0][first]
            if c == 0 or back[first] == 0 or c + s[first] + back[first] > T:
                return None
            tu = c + s[first]; vis[first] = 1; route.append(first); cur = first
        while True:
            row = rows[cur]; bj = -1; bp = 0; bc = 1; rem = T - tu
            for j in range(1, N):
                if vis[j]:
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
            tu += row[bj] + s[bj]; vis[bj] = 1; route.append(bj); cur = bj
        return route + [0]

    best = 0; best_path = [0, 0]
    for first in [None] + list(range(1, N)):
        r = greedy_from(first)
        if r is not None and reward(r) > best:
            best = reward(r); best_path = r

    def bound(mask, time_used):
        cap = T - time_used - min_back
        if cap < 0:
            return 0
        b = 0; k = 0
        while k < M:
            if not (mask >> order[k] & 1):
                f = of[k]
                if f <= cap:
                    b += op[k]; cap -= f
                else:
                    b += op[k] * cap // f
                    break
            k += 1
        return b

    # ---------- Held-Karp 狀態 DP：dp[(mask,last)] = 到達該子集且結尾在 last 的最短時間 ----------
    # 以深度優先順序填表(迭代式 stack)，搭配 incumbent + 分數背包上界剪枝；
    # 支配規則：同 (mask,last) 只保留最短時間的狀態，其餘剪除。保證求得精確最佳解。
    BIG = 1 << 62
    use_flat = ((1 << N) * N <= 5_000_000)
    if use_flat:
        memo = [BIG] * ((1 << N) * N)
    else:
        memo = {}
    NK = N
    Tl = T
    # stack 元素：(cur, mask, time_used, reward, path_tuple)
    stack = [(0, 1, 0, 0, (0,))]
    while stack:
        cur, mask, tu, rew, path = stack.pop()
        if cur != 0:
            bk = back[cur]
            if bk != 0 and tu + bk <= Tl and rew > best:
                best = rew; best_path = list(path) + [0]
        if rew + bound(mask, tu) <= best:
            continue
        for j, c, sj, pj, bj in adj[cur]:
            if mask & bj:
                continue
            nt = tu + c + sj
            if nt > Tl:
                continue
            key = (mask | bj) * NK + j
            if use_flat:
                if memo[key] <= nt:
                    continue
                memo[key] = nt
            else:
                pv = memo.get(key)
                if pv is not None and pv <= nt:
                    continue
                memo[key] = nt
            stack.append((j, mask | bj, nt, rew + pj, path + (j,)))

    # ---------- 合法性安全網 ----------
    def is_legal(route):
        if len(route) < 2 or route[0] != 0 or route[-1] != 0:
            return False
        seen = set(); t = 0
        for k in range(len(route) - 1):
            a = route[k]; b = route[k + 1]
            if a == b or rows[a][b] == 0:
                return False
            t += rows[a][b]
            if b != 0:
                if b in seen:
                    return False
                seen.add(b); t += s[b]
        return t <= Tl

    if not (is_legal(best_path) and reward(best_path) == best):
        best = 0; best_path = [0, 0]
        for first in [None] + list(range(1, N)):
            r = greedy_from(first)
            if r is not None and is_legal(r) and reward(r) > best:
                best = reward(r); best_path = r

    out = sys.stdout
    out.write(str(best)); out.write("\n")
    out.write(" ".join(map(str, best_path))); out.write("\n")


main()
