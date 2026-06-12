import sys, time

START = time.time()
BUDGET = 6.5  


def main():
    data = sys.stdin.buffer.read().split()
    pos = 0
    N = int(data[pos]); pos += 1
    T_max = int(data[pos]); pos += 1
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

    def travel(r):
        return sum(rows[r[k]][r[k + 1]] for k in range(len(r) - 1))

    def rtime(r):
        t = travel(r)
        for b in r[1:-1]:
            t += s[b]
        return t

    visited = bytearray(N); visited[0] = 1
    route = [0]; cur = 0
    for _ in range(N - 1):
        ru = rows[cur]; best = -1; bc = None
        for j in range(N):
            if visited[j] or j == cur:
                continue
            c = ru[j]
            if c == 0:
                continue
            if bc is None or c < bc:
                bc = c; best = j
        if best == -1:
            break
        visited[best] = 1; route.append(best); cur = best
    if rows[cur][0] == 0:
        for idx in range(len(route) - 2, 0, -1):
            if rows[route[idx]][0] != 0:
                route.append(route.pop(idx)); break
    route.append(0)

    def insert_unvisited():
        changed = True
        while changed:
            changed = False
            for j in range(1, N):
                if visited[j]:
                    continue
                bestk = -1; bestadd = None
                for k in range(len(route) - 1):
                    a = route[k]; b = route[k + 1]
                    aj = rows[a][j]
                    if aj == 0:
                        continue
                    jb = rows[j][b]
                    if jb == 0:
                        continue
                    add = aj + jb - rows[a][b]
                    if bestadd is None or add < bestadd:
                        bestadd = add; bestk = k
                if bestk != -1:
                    route.insert(bestk + 1, j); visited[j] = 1; changed = True
    insert_unvisited()

    def oropt(deadline):
        improved = True
        while improved and time.time() < deadline:
            improved = False
            for seg in (1, 2, 3):
                i = 1
                while i + seg <= len(route) - 1:
                    a = route[i - 1]; b = route[i + seg]
                    rab = rows[a][b]
                    if rab == 0:
                        i += 1; continue
                    x0 = route[i]; x1 = route[i + seg - 1]
                    removed = rows[a][x0] + rows[x1][b] - rab
                    if removed <= 0:
                        i += 1; continue
                    R = route; bestpos = -1; bestadd = removed
                    for k in range(len(R) - 1):
                        if i - 1 <= k <= i + seg - 1:
                            continue
                        c = R[k]; d = R[k + 1]
                        r1 = rows[c][x0]
                        if r1 == 0:
                            continue
                        r2 = rows[x1][d]
                        if r2 == 0:
                            continue
                        add = r1 + r2 - rows[c][d]
                        if add < bestadd:
                            bestadd = add; bestpos = k
                    if bestpos != -1:
                        seg_nodes = route[i:i + seg]; del route[i:i + seg]
                        if bestpos > i:
                            bestpos -= seg
                        route[bestpos + 1:bestpos + 1] = seg_nodes
                        improved = True
                    else:
                        i += 1

    def twoopt(deadline, W=40):
        n = len(route); improved = True
        while improved and time.time() < deadline:
            improved = False
            n = len(route)
            for i in range(1, n - 2):
                a = route[i - 1]; xi = route[i]; raxi = rows[a][xi]
                jmax = i + W
                if jmax > n - 1:
                    jmax = n - 1
                for j in range(i + 1, jmax):
                    xj = route[j]; b = route[j + 1]
                    e1 = rows[a][xj]
                    if e1 == 0:
                        continue
                    e2 = rows[xi][b]
                    if e2 == 0:
                        continue
                    ok = True; oi = 0; ni = 0
                    for k in range(i, j):
                        oi += rows[route[k]][route[k + 1]]
                        rk = rows[route[k + 1]][route[k]]
                        if rk == 0:
                            ok = False; break
                        ni += rk
                    if not ok:
                        continue
                    if e1 + e2 + ni < raxi + rows[xj][b] + oi:
                        route[i:j + 1] = route[i:j + 1][::-1]
                        improved = True
                        xi = route[i]; raxi = rows[a][xi]

    dl = START + BUDGET
    oropt(dl); twoopt(dl); oropt(dl)

    def trim():
        cur_t = rtime(route)
        while cur_t > T_max and len(route) > 2:
            bestk = -1; w_p = 1; w_saved = 0
            for k in range(1, len(route) - 1):
                a = route[k - 1]; x = route[k]; b = route[k + 1]
                if rows[a][b] == 0:
                    continue
                saved = rows[a][x] + s[x] + rows[x][b] - rows[a][b]
                if saved <= 0:
                    saved = 1
                px = p[x]
                if bestk == -1 or px * w_saved < w_p * saved:
                    bestk = k; w_p = px; w_saved = saved
            if bestk == -1:
                break
            a = route[bestk - 1]; x = route[bestk]; b = route[bestk + 1]
            cur_t -= (rows[a][x] + s[x] + rows[x][b] - rows[a][b])
            del route[bestk]

    if rtime(route) > T_max:
        twoopt(dl); oropt(dl)
        if rtime(route) > T_max:
            trim()

    def fill_within_budget():
        t_used = rtime(route)
        changed = True
        while changed and time.time() < dl:
            changed = False
            inroute = bytearray(N)
            for x in route:
                inroute[x] = 1
            bestk = -1; bestj = -1; best_extra = None
            for j in range(1, N):
                if inroute[j]:
                    continue
                for k in range(len(route) - 1):
                    a = route[k]; b = route[k + 1]
                    aj = rows[a][j]
                    if aj == 0:
                        continue
                    jb = rows[j][b]
                    if jb == 0:
                        continue
                    extra = aj + s[j] + jb - rows[a][b]
                    if t_used + extra > T_max:
                        continue
                    if best_extra is None or extra < best_extra:
                        best_extra = extra; bestk = k; bestj = j
            if bestj != -1:
                route.insert(bestk + 1, bestj); t_used += best_extra; changed = True
    if rtime(route) <= T_max:
        fill_within_budget()

    def is_legal(r):
        if r[0] != 0 or r[-1] != 0:
            return False
        seen = set(); t = 0
        for k in range(len(r) - 1):
            a = r[k]; b = r[k + 1]
            if a == b or rows[a][b] == 0:
                return False
            t += rows[a][b]
            if b != 0:
                if b in seen:
                    return False
                seen.add(b); t += s[b]
        return t <= T_max

    if not is_legal(route):
        back = [rows[i][0] for i in range(N)]
        vis = bytearray(N); vis[0] = 1; cur = 0; tu = 0; route = [0]
        while True:
            row = rows[cur]; bj = -1; bp = 0; bc = 1; rem = T_max - tu
            for j in range(1, N):
                if vis[j]:
                    continue
                tij = row[j]
                if tij == 0:
                    continue
                bk = back[j]
                if bk == 0:
                    continue
                cost = tij + s[j]
                if cost + bk > rem:
                    continue
                pj = p[j]
                if bj == -1 or pj * bc > bp * cost:
                    bj = j; bp = pj; bc = cost
            if bj == -1:
                break
            tu += row[bj] + s[bj]; vis[bj] = 1; route.append(bj); cur = bj
        route.append(0)

    total = sum(p[x] for x in route if x != 0)
    out = sys.stdout
    out.write(str(total)); out.write("\n")
    out.write(" ".join(map(str, route))); out.write("\n")


main()
