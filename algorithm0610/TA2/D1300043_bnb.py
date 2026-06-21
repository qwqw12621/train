import sys, heapq

# ============================================================================
# 限時獎勵收集配送 — 分支界限 Branch and Bound (最佳優先 best-first)
# 與回溯法的差別：回溯=DFS+剪枝；BnB=用優先佇列「依樂觀上界」優先展開最有希望
# 的部分解，並用「上界 <= 現有最佳」剪枝；最佳優先下，一旦佇列頂端上界都贏不了
# 現有最佳，即可證明最佳並提前結束。
#
# 【高效率撰寫要點】（教學重點，程式中以 ★ 標註）
#  ★1 位元遮罩(bitmask) 表示「已訪集合」：N<=17 用一個整數即可，
#      成員判斷/加入/雜湊都是 O(1)，比 set/list 快很多、省記憶體。
#  ★2 緊的可採納上界(admissible bound)：界越緊、剪枝越多。這裡用
#      「剩餘時間最多再容納 kmax 個客戶 × 最大獎勵」。
#  ★3 先用貪婪求初始下界(incumbent)：一開始就有好的最佳值，剪枝更早生效。
#  ★4 最佳優先 + 提前停止：堆積頂端(上界最大者)都 <= 最佳 → 全部免談，結束。
#  ★5 支配剪枝(dominance)：同一(頂點, 已訪集合)若以更少時間到達即支配，
#      用 dict 記錄每個狀態的最短到達時間，劣於既有者直接丟棄。
# ============================================================================

def main():
    d = sys.stdin.buffer.read().split()
    N=int(d[0]); Tmax=int(d[1]); idx=2
    p=[0]*N; s=[0]*N
    for i in range(N): p[i]=int(d[idx]); s[i]=int(d[idx+1]); idx+=2
    t=[None]*N
    for i in range(N):
        b=idx+i*N; t[i]=[int(x) for x in d[b:b+N]]
    del d
    INF=1<<60

    # dist_to_depot[j]：j 回倉庫 0 的最短距離（反向圖陣列版 Dijkstra），
    # 作「之後仍能回倉庫」的可採納可行性下界。
    dist=[INF]*N; dist[0]=0; fin=bytearray(N)
    for _ in range(N):
        u=-1; bd=INF
        for v in range(N):
            if not fin[v] and dist[v]<bd: bd=dist[v]; u=v
        if u<0: break
        fin[u]=1
        for v in range(N):
            w=t[v][u]
            if w and bd+w<dist[v]: dist[v]=bd+w

    # 上界用的常數：每多訪 1 客戶至少花「最便宜邊 + 最小服務」
    pe=[t[i][j] for i in range(N) for j in range(N) if i!=j and t[i][j]]
    mine=min(pe) if pe else 1
    mins=min((s[j] for j in range(1,N)), default=0)
    step=mine+mins if mine+mins>0 else 1
    maxp=max(p) if p else 0

    def upper_bound(tused, rew):                 # ★2 樂觀上界
        avail=Tmax-tused-mine                    # 預留一條最便宜回程邊
        kmax=avail//step if avail>0 else 0
        return rew+kmax*maxp

    best_reward=0; best_path=[0,0]

    # ★3 貪婪初始下界
    seen=bytearray(N); seen[0]=1; cur=0; tu=0; rew=0; gp=[0]
    while True:
        bj=-1; bn=0; bden=0; tc=t[cur]
        for j in range(N):
            if seen[j] or not tc[j]: continue
            nt=tu+tc[j]+s[j]
            if nt+dist[j]>Tmax: continue
            dt=tc[j]+s[j]
            if bj<0 or p[j]*bden>bn*dt: bj=j; bn=p[j]; bden=dt
        if bj<0: break
        seen[bj]=1; tu+=tc[bj]+s[bj]; rew+=p[bj]; cur=bj; gp.append(bj)
    if cur!=0 and t[cur][0] and tu+t[cur][0]<=Tmax:
        best_reward=rew; best_path=gp+[0]

    # ★1 bitmask 已訪集合；★4 最佳優先優先佇列（用 -bound 取最大）
    # 節點：(-bound, 序號, 頂點, mask, 時間, 獎勵, 路徑tuple)
    start_mask=1                                 # 已訪 {0}
    pq=[(-upper_bound(0,0), 0, 0, start_mask, 0, 0, (0,))]
    seq=1
    best_time={}                                 # ★5 支配：(頂點,mask)->最短到達時間

    while pq:
        nb, _, v, mask, tu, rew, path = heapq.heappop(pq)
        bound=-nb
        # ★4 提前停止：頂端上界都 <= 最佳 → 不可能更好，證明最佳，結束
        if bound<=best_reward: break
        # 解答檢查：能合法回倉庫即為完整解
        if v!=0:
            back=t[v][0]
            if back and tu+back<=Tmax and rew>best_reward:
                best_reward=rew; best_path=list(path)+[0]
        # 分支：展開每個可達、可行、未訪的客戶
        tc=t[v]
        for j in range(N):
            if (mask>>j)&1: continue
            e=tc[j]
            if not e: continue                    # 可行性：須為實路
            nt=tu+e+s[j]
            if nt+dist[j]>Tmax: continue          # 可行性：之後仍能回倉庫
            nrew=rew+p[j]
            ub=upper_bound(nt, nrew)
            if ub<=best_reward: continue          # 界限剪枝
            nmask=mask|(1<<j)
            key=(j,nmask)                         # ★5 支配剪枝
            pt=best_time.get(key)
            if pt is not None and pt<=nt: continue
            best_time[key]=nt
            heapq.heappush(pq,(-ub, seq, j, nmask, nt, nrew, path+(j,)))
            seq+=1

    w=sys.stdout.write
    if best_reward<=0: w("0\n0 0\n")
    else: w(str(best_reward)); w("\n"); w(" ".join(map(str,best_path))); w("\n")

main()
