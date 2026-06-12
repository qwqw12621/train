import sys, time, random

def main():
    st = time.time()
    d = sys.stdin.buffer.read().split()
    N=int(d[0]); Tmax=int(d[1]); idx=2
    p=[0]*N; s=[0]*N
    for i in range(N): p[i]=int(d[idx]); s[i]=int(d[idx+1]); idx+=2
    t=[None]*N
    for i in range(N):
        b=idx+i*N; t[i]=[int(x) for x in d[b:b+N]]
    del d
    INF=1<<60
    succ=[0]*N; pred=[0]*N; inr=bytearray(N); inr[0]=1

    # 1) 最近鄰：用最便宜的邊把節點串起來
    cur=0; order=[0]
    while True:
        tc=t[cur]; best=INF; bn=-1
        for j in range(N):
            if not inr[j] and tc[j] and tc[j]<best: best=tc[j]; bn=j
        if bn<0: break
        inr[bn]=1; order.append(bn); cur=bn
    for i in range(len(order)-1): succ[order[i]]=order[i+1]; pred[order[i+1]]=order[i]
    succ[order[-1]]=0; pred[0]=order[-1]

    # 2) 未串到的點用最便宜插入放進環
    def ci(k):
        best=INF; bl=-1; a=0; tk=t[k]
        while True:
            b=succ[a]; ta=t[a]; tak=ta[k]
            if tak:
                tkb=tk[b]
                if tkb or k==b:
                    dd=tak+tkb-ta[b]
                    if dd<best: best=dd; bl=a
            a=b
            if a==0: break
        return bl
    for k in range(1,N):
        if not inr[k]:
            a=ci(k)
            if a>=0:
                b=succ[a]; succ[a]=k; succ[k]=b; pred[k]=a; pred[b]=k; inr[k]=1

    def trav():
        a=0; tot=0
        while True:
            b=succ[a]; tot+=t[a][b]; a=b
            if a==0: break
        return tot

    # Or-opt(L)：整段(不反轉)搬到更省「行駛」的位置；只換 3 邊，皆須實路
    def oropt(L):
        imp=False; h=succ[0]
        while h!=0:
            tail=h; ok=True
            for _ in range(L-1):
                tail=succ[tail]
                if tail==0: ok=False; break
            if not ok: break
            nxt=succ[tail]; pv=pred[h]; nv=succ[tail]; br=t[pv][nv]
            if br or pv==nv:
                saved=t[pv][h]+t[tail][nv]-br
                if saved>0:
                    bg=0; ba=-1; a=0; tt=t[tail]
                    while True:
                        b=succ[a]; ins=False; x=h
                        while True:
                            if a==x or b==x: ins=True; break
                            if x==tail: break
                            x=succ[x]
                        if not(ins or (a==pv and b==nv)):
                            ta=t[a]; tah=ta[h]
                            if tah:
                                ttb=tt[b]
                                if ttb:
                                    g=saved-(tah+ttb-ta[b])
                                    if g>bg: bg=g; ba=a
                        a=b
                        if a==0: break
                    if ba>=0:
                        succ[pv]=nv; pred[nv]=pv; bb=succ[ba]
                        succ[ba]=h; pred[h]=ba; succ[tail]=bb; pred[bb]=tail; imp=True
            h=nxt
        return imp
    def localmin():
        while True:
            if not(oropt(1)|oropt(2)|oropt(3)|oropt(4)): break

    serv_all=sum(s[1:])
    need=Tmax-serv_all                 # 全服務所允許的最大行駛

    localmin()
    best_t=trav(); best_succ=succ[:]

    # 3) 迭代局部搜尋：擾動+再 localmin，壓短行駛；一旦可全服務即停
    DEADLINE=st+4.5                    # 安全時限（留餘裕給較慢的評分機）
    random.seed(1)
    nodes=list(range(1,N))
    while best_t>need and N>5 and time.time()<DEADLINE:
        for _ in range(3):             # 擾動：隨機搬幾個點到隨機合法位置
            v=random.choice(nodes); pv=pred[v]; nv=succ[v]
            if pv!=nv and not t[pv][nv]: continue
            tries=0
            while tries<8:
                a=random.choice(nodes) if random.random()<0.9 else 0
                if a==v: tries+=1; continue
                b=succ[a]
                if b==v: tries+=1; continue
                if t[a][v] and t[v][b]:
                    succ[pv]=nv; pred[nv]=pv
                    succ[a]=v; pred[v]=a; succ[v]=b; pred[b]=v
                    break
                tries+=1
        localmin()
        tt=trav()
        if tt<best_t:
            best_t=tt; best_succ=succ[:]
        else:                          # 回復最短
            succ[:]=best_succ; a=0
            while True:
                b=succ[a]; pred[b]=a; a=b
                if a==0: break

    succ[:]=best_succ; a=0
    while True:
        b=succ[a]; pred[b]=a; a=b
        if a==0: break

    # 4) 若仍超預算，移除「省時最多/損獎勵最少」的客戶到剛好塞進（橋接邊須實路）
    total=best_t+serv_all
    def free_time(v):
        pv=pred[v]; nv=succ[v]; br=t[pv][nv]
        if not (br or pv==nv): return None
        return s[v]+t[pv][v]+t[v][nv]-br
    while total>Tmax:
        bv=-1; bk=None; v=succ[0]
        while v!=0:
            g=free_time(v)
            if g is not None and g>0:
                key=g if p[v]==0 else g/p[v]   # 省最多時間、丟最少獎勵
                if bk is None or key>bk: bk=key; bv=v
            v=succ[v]
        if bv<0: break
        v=bv; pv=pred[v]; nv=succ[v]; g=free_time(v)
        succ[pv]=nv; pred[nv]=pv; total-=g

    route=[0]; a=succ[0]
    while a!=0: route.append(a); a=succ[a]
    route.append(0)
    tot=0
    for n in route: tot+=p[n]
    w=sys.stdout.write
    w(str(tot)); w("\n"); w(" ".join(map(str,route))); w("\n")

main()
