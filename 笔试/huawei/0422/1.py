
import sys
from collections import deque
"""
3 1 500
0 0 10 100 50
1 0 20 100 50
0 1 30 100 50
输出：0

4 1 150
0 0 10 100 10
1 0 20 100 10
5 5 10 200 100
5 6 30 200 100
输出：200
"""
def main():
    N, dist, W_threshold  = map(int, input().strip().split())
    base = []
    for i in range(N):
        x, y, t, w, user = map(int, input().strip().split())
        base.append([x, y, t, w, user])

    # 步骤一 计算直接关系
    direct = [[False for _ in range(N)] for _ in range(N)]
    for i in range(N):
        x1,y1,_, _,_ = base[i]
        for j in range(i+1, N):
            x2,y2,_, _,_ = base[j]
            if abs(x1-x2) + abs(y1-y2) <= dist:
                direct[i][j] =  True
                direct[j][i] =  True

    # 步骤二 筛选关键节点
    keys_bases = [] # 关键节点
    idx_map = [-1]*N # 节点映射
    for i in range(N):
        sum_w= base[i][3]
        for j in range(N):
            if direct[i][j]:
                sum_w += base[j][3]
        if sum_w >= W_threshold:
            idx_map[i] = len(keys_bases)
            keys_bases.append(base[i])

    m = len(keys_bases)
    if m == 0:
        print(0)
        return

    # 步骤三 构建有向图和拓扑排序
    adj = [[] for _ in range(len(keys_bases))]
    in_degree = [0]*m # 节点入度
    for i in range(m):
        for j in range(i+1, m):
            # 找到原索引
            u_orig = idx_map[i]
            v_orig = idx_map[j]
            for k in range(N):
                if idx_map[k] == i:
                    u_orig = k
                if idx_map[k] == j:
                    v_orig = k

            # 检查直接关联性
            if direct[u_orig][v_orig]:
                t_j= keys_bases[j][2]
                t_i= keys_bases[i][2]
                if t_j > t_i:
                    adj[i].append(j)
                    in_degree[j] += 1
                elif t_j < t_i:
                    adj[j].append(i)
                    in_degree[i] += 1
     # 拓扑排序
    q = deque()
    topo = [] # 拓扑序列
    for i in range(m):
        if in_degree[i] == 0:
            q.append(i) # 添加入度为0的节点
    while q:
        u = q.popleft()
        topo.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)

    # 步骤四 动态规划求最短路径
    dp = [0] *  m
    max_user = 0
    for i in topo:
        max_user = max(max_user, keys_bases[i][4])
        if i == 0:
            dp[i] = keys_bases[i][4]
        else:
            dp[i] = max(dp[i-1], keys_bases[i][4])
    for u in range(m):
        for v in adj[u]:
            if dp[v] < dp[u] + keys_bases[v][4]:
                dp[v] = dp[u] + keys_bases[v][4]
                if dp[v] > max_user:
                    max_user = dp[v]
    print(max_user)

if __name__ == '__main__':
    main()








