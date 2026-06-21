import sys


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    N = int(data[pos]); pos += 1
    T = int(data[pos]); pos += 1
    p = [0] * N; s = [0] * N
    for i in range(N):
        p[i] = int(data[pos]); pos += 1
        s[i] = int(data[pos]); pos += 1
    rows = [None] * N
    for i in range(N):
        b = pos + i * N
        rows[i] = [int(x) for x in data[b:b + N]]
    pos += N * N
    del data

    back = [rows[i][0] for i in range(N)]
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

    # 上界：依 prize/footprint 由大到小的分數背包（mask-aware）
    ob = sorted((j for j in range(1, N) if foot[j] < (1 << 62)),
                key=lambda j: (-p[j] / foot[j], foot[j]))
    M = len(ob)
    of = [foot[j] for j in ob]
    op = [p[j] for j in ob]
    obit = [1 << j for j in ob]

    def bound(mask, time_used):
        cap = T - time_used - min_back
        if cap < 0:
            return 0
        b = 0
        for k in range(M):
            if mask & obit[k]:
                continue
            f = of[k]
            if f <= cap:
                b += op[k]; cap -= f
            else:
                b += op[k] * cap // f
                break
        return b

    order = sorted(range(1, N), key=lambda j: -p[j])
    adj = [[(j, rows[i][j], s[j], p[j]) for j in order if rows[i][j] != 0] for i in range(N)]

    # ---- 多起點比值貪婪：強 incumbent ----
    def greedy_from(first):
        vis = bytearray(N); vis[0] = 1; cur = 0; tu = 0; rew = 0; route = [0]
        if first is not None:
            c = rows[0][first]
            if c == 0 or back[first] == 0 or c + s[first] + back[first] > T:
                return 0, None
            tu = c + s[first]; rew = p[first]; vis[first] = 1; route.append(first); cur = first
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
            tu += row[bj] + s[bj]; rew += p[bj]; vis[bj] = 1; route.append(bj); cur = bj
        return rew, route + [0]

    best = 0; best_path = [0, 0]
    for first in [None] + list(range(1, N)):
        r, rt = greedy_from(first)
        if rt is not None and r > best:
            best = r; best_path = rt

    # ---- 桶式最佳優先 branch and bound（Dial 變形；只用 sys，無 heapq）----
    # buckets[ub] = list of state ids；curmax 為目前最大上界，可上升（因取整使 child 上界偶爾上浮）
    st_cur = [0]; st_mask = [1]; st_tu = [0]; st_par = [-1]; st_node = [0]; st_rew = [0]
    use_flat = (1 << N) * N <= 8_000_000
    BIG = 1 << 62
    memo = [BIG] * ((1 << N) * N) if use_flat else {}
    memo_get = None if use_flat else memo.get

    NB = N
    root_ub = bound(1, 0)
    buckets = {root_ub: [0]}
    curmax = root_ub
    best_par = -1; best_last = -1

    while curmax > best:
        bl = buckets.get(curmax)
        if not bl:
            del buckets[curmax]
            # 下降到下一個非空桶
            if buckets:
                curmax = max(buckets)
                continue
            else:
                break
        sid = bl.pop()
        cur = st_cur[sid]; mask = st_mask[sid]; tu = st_tu[sid]; reward = st_rew[sid]
        kc = mask * NB + cur
        if use_flat:
            if memo[kc] < tu:
                continue
        else:
            if memo_get(kc, BIG) < tu:
                continue
        for j, c, sj, pj in adj[cur]:
            bit = 1 << j
            if mask & bit:
                continue
            nt = tu + c + sj
            if nt > T:
                continue
            nmask = mask | bit
            key = nmask * NB + j
            if use_flat:
                if memo[key] <= nt:
                    continue
                memo[key] = nt
            else:
                pv = memo_get(key)
                if pv is not None and pv <= nt:
                    continue
                memo[key] = nt
            nr = reward + pj
            bj = back[j]
            if bj != 0 and nt + bj <= T and nr > best:
                best = nr; best_par = sid; best_last = j
            ub = nr + bound(nmask, nt)
            if ub > best:
                nid = len(st_cur)
                st_cur.append(j); st_mask.append(nmask); st_tu.append(nt)
                st_par.append(sid); st_node.append(j); st_rew.append(nr)
                blk = buckets.get(ub)
                if blk is None:
                    buckets[ub] = [nid]
                else:
                    blk.append(nid)
                if ub > curmax:
                    curmax = ub

    if best_par != -1:
        nodes = []; x = best_par
        while x != -1:
            nodes.append(st_node[x]); x = st_par[x]
        nodes.reverse()
        best_path = nodes + [best_last, 0]

    sys.stdout.write(str(best) + "\n")
    sys.stdout.write(" ".join(map(str, best_path)) + "\n")


main()
