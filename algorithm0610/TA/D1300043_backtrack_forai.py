import sys

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

    dist=[INF]*N; dist[0]=0; done=bytearray(N)
    for _ in range(N):
        u=-1; bd=INF
        for v in range(N):
            if not done[v] and dist[v]<bd: bd=dist[v]; u=v
        if u<0: break
        done[u]=1
        for v in range(N):
            w=t[v][u]
            if w and bd+w<dist[v]: dist[v]=bd+w

    best_reward=[0]; best_path=[[0,0]]

    served=bytearray(N); served[0]=1
    cur=0; tused=0; rew=0; gp=[0]
    while True:
        bj=-1; bn=0; bden=0; tc=t[cur]
        for j in range(N):
            if served[j]: continue
            e=tc[j]
            if not e: continue
            nt=tused+e+s[j]
            if nt+dist[j]>Tmax: continue
            dt=e+s[j]
            if bj<0 or p[j]*bden>bn*dt: 
                bj=j; bn=p[j]; bden=dt
        if bj<0: break
        served[bj]=1; tused+=tc[bj]+s[bj]; rew+=p[bj]; cur=bj; gp.append(bj)
    if cur!=0 and t[cur][0] and tused+t[cur][0]<=Tmax:
        best_reward[0]=rew; best_path[0]=gp+[0]

    posedges=[t[i][j] for i in range(N) for j in range(N) if i!=j and t[i][j]]
    mine=min(posedges) if posedges else 1
    mins=min((s[j] for j in range(1,N)), default=0)
    step=mine+mins if mine+mins>0 else 1
    maxp=max(p) if p else 0

    visited=bytearray(N); visited[0]=1
    path=[0]
    NODECAP=2000000               
    cnt=[0]
    sys.setrecursionlimit(10000)

    def dfs(cur, tused, rew):
        if cur!=0:
            back=t[cur][0]
            if back and tused+back<=Tmax and rew>best_reward[0]:
                best_reward[0]=rew; best_path[0]=path+[0]
        cnt[0]+=1
        if cnt[0]>NODECAP: return
        avail=Tmax-tused-mine
        kmax=avail//step if avail>0 else 0
        if rew+kmax*maxp<=best_reward[0]: return
        tc=t[cur]
        cand=[]
        for j in range(N):
            if visited[j]: continue
            e=tc[j]
            if not e: continue                 
            nt=tused+e+s[j]
            if nt+dist[j]>Tmax: continue        
            cand.append((p[j],j,nt))
        cand.sort(reverse=True)
        for pj,j,nt in cand:
            visited[j]=1; path.append(j)
            dfs(j, nt, rew+pj)                 
            path.pop(); visited[j]=0         

    dfs(0,0,0)

    w=sys.stdout.write
    if best_reward[0]<=0:
        w("0\n0 0\n")
    else:
        w(str(best_reward[0])); w("\n"); w(" ".join(map(str,best_path[0]))); w("\n")

main()
