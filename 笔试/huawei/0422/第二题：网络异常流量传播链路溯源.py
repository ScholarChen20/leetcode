"""
在网络监控中，异常流量的流动通常具有局部聚集性。需要识别出高负载的基站（关键节点），并判断流量在这些节点之间定向传播链的最长路径。
给定 $N$ 个基站，每个基站包含坐标 $(x_i, y_i)$、时间戳 $t_i$、负载 $w_i$ 和用户数 $u_i$。
#### 判定规则
1. **直接关联**：若两个基站的曼哈顿距离 $\le \varepsilon$，即 $|x_i - x_j| + |y_i - y_j| \le \varepsilon$，则这两个基站直接关联。
2. **关键节点**：若一个基站及其所有直接关联的基站（含自身）的负载之和 $\ge W$，则该基站为关键节点。
3. **链路条件**：两个关键节点之间必须直接关联，且时间戳不同，才能建立有向链路。流量总是从时间早的节点流向时间晚的节点；若时间相同则无法建立链路。
4. **传播链条**：由一系列关键节点通过有向链路首尾相连构成的路径。链条的规模定义为路径上所有节点的用户数 $u$ 之和。
#### 求解目标
计算全网中所有传播链条能覆盖的**最大用户总数**。
*注意：若无法形成任何传播链条（即路径长度至少需要包含 2 个节点），则输出 0。*
#### 输入格式
第一行包含三个整数/实数：$N$、$\varepsilon$、$W$。
接下来 $N$ 行，每行包含 5 个数值，分别为：$x_i, y_i, t_i, w_i, u_i$。


**样例 1**
输入：
3 1 500
0 0 10 100 50
1 0 20 100 50
0 1 30 100 50
输出：0

**样例 2**
输入：
4 1 150
0 0 10 100 10
1 0 20 100 10
5 5 10 200 100
5 6 30 200 100
输出：200
"""
import sys

input = sys.stdin.readline

line = input().split()
N, eps_dist, w_threshold = int(line[0]), int(line[1]), int(line[2])

stations = []
for _ in range(N):
    parts = list(map(int, input().split()))
    stations.append(parts)

adj = [[False] * N for _ in range(N)]
for i in range(N):
    for j in range(i + 1, N):
        dist = abs(stations[i][0] - stations[j][0]) + abs(stations[i][1] - stations[j][1])
        if dist <= eps_dist:
            adj[i][j] = True
            adj[j][i] = True

is_key = [False] * N
for i in range(N):
    total_w = stations[i][3]
    for j in range(N):
        if i != j and adj[i][j]:
            total_w += stations[j][3]
    if total_w >= w_threshold:
        is_key[i] = True

key_nodes = [i for i in range(N) if is_key[i]]
key_nodes.sort(key=lambda i: stations[i][2])

m = len(key_nodes)
f = [stations[key_nodes[i]][4] for i in range(m)]

ans = 0
for j in range(m):
    nj = key_nodes[j]
    for i in range(j):
        ni = key_nodes[i]
        if adj[ni][nj] and stations[ni][2] < stations[nj][2]:
            f[j] = max(f[j], f[i] + stations[nj][4])
            ans = max(ans, f[j])

print(ans)

"""
思路分析

本题的解题逻辑可以清晰地划分为两个阶段：前半段为预处理（根据规则筛选关键节点），后半段为算法核心（在关键节点构成的有向无环图上通过动态规划寻找最优链）。

第一步：构建邻接关系
由于基站数量 N le 1000，数据规模允许使用 O(N^2) 的复杂度。可以通过两层 for 循环遍历所有基站对，检查它们的曼哈顿距离是否满足 |x_i - x_j| + |y_i - y_j| le varepsilon。如果满足条件，则使用一个二维布尔数组 adj[i][j] 记录下这两个基站存在直接关联。

第二步：筛选关键节点
遍历每一个基站 i，将其自身的负载 w_i 加上所有与其直接关联的邻居基站的负载。如果这个邻域负载总和 ge W，则将该基站标记为“关键节点”。

样例 1 分析：3 个基站两两关联（距离均 le 1），每个基站的邻域负载和均为 100+100+100=300。由于 300 < 500，因此没有任何基站满足关键节点条件，最终输出 0。
样例 2 分析：基站 0 和 1 关联，基站 2 和 3 关联。基站 2 的邻域负载和为 200+200=400 ge 150，基站 3 同理。因此基站 2 和 3 被成功标记为关键节点。

第三步：DAG 最长路动态规划 (DP)
由于流量只能从时间早的基站传向时间晚的基站，且不会折返，这天然构成了一个有向无环图（DAG）。

拓扑排序：将所有筛选出的关键节点按照时间戳 t 从小到大进行排序，排序后的顺序即为该 DAG 的拓扑序。
状态定义：定义 f[j] 表示以第 j 个关键节点作为传播链的最后一站时，链上所有节点的用户数 u 之和的最大值。
状态初始化：初始状态下，每个节点都可以独立成链，因此 f[j] = u_j。
状态转移：按照时间顺序从前往后处理每个节点 j，回头遍历排在它前面的每一个节点 i。如果节点 i 和节点 j 存在直接关联（adj[i][j] == True），且时间严格递增（t_i < t_j），则执行状态转移：
    f[j] = max(f[j],  f[i] + u_j)
最终答案：题目要求传播链条至少包含 2 个节点。因此，最终答案只统计那些被边成功更新过的 f[j]（即 f[j] > u_j 的情况）中的最大值。如果没有任何节点被更新，则输出 0。
"""