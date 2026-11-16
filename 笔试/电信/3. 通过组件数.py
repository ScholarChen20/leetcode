"""
我们需要在 01 网格中找出所有的极大 4 连通块（组件），并计算每个组件的：
大小：组件中格子数（即 1 的个数）。
周长：组件格子与网格外或 0 格子相邻的边数。
然后，根据条件筛选出“通过门票检查”的组件（大小为奇数且周长为偶数），并统计：
通过组件数。
通过组件格子总数。
最大通过组件周长（若无通过组件，输出 0）。
若没有通过门票检查的组件，三个整数均输出 0。

示例1：
输入：
1 1
1
输出： 1 1 4
示例2：
输入：
2 2
11
00
输出：0 0 0
"""

import sys
# 增加递归深度，防止 DFS 递归过深
sys.setrecursionlimit(100000)
def solve():
    # 读取 n 和 m
    line1 = sys.stdin.readline().split()
    if not line1:
        return
    n, m = map(int, line1)

    grid = []
    for _ in range(n):
        grid.append(sys.stdin.readline().strip())

    visited = [[False] * m for _ in range(n)]

    # 四个方向：上、下、左、右
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    valid_count = 0  # 通过组件数
    total_cells = 0  # 通过组件格子总数
    max_perimeter = 0  # 最大通过组件周长

    def dfs(r, c):
        nonlocal size, perimeter
        visited[r][c] = True
        size += 1  # 当前格子计入大小

        # 检查四个方向
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= n or nc < 0 or nc >= m:
                # 邻居是边界外，计入周长
                perimeter += 1
            elif grid[nr][nc] == '0':
                # 邻居是 0，计入周长
                perimeter += 1
            else:
                # 邻居是 1，若未访问，继续 DFS
                if not visited[nr][nc]:
                    dfs(nr, nc)

    for i in range(n):
        for j in range(m):
            if grid[i][j] == '1' and not visited[i][j]:
                size = 0
                perimeter = 0
                dfs(i, j)

                # 判断是否通过门票检查
                if size % 2 == 1 and perimeter % 2 == 0:
                    valid_count += 1
                    total_cells += size
                    if perimeter > max_perimeter:
                        max_perimeter = perimeter

    if valid_count == 0:
        print("0 0 0")
    else:
        print(f"{valid_count} {total_cells} {max_perimeter}")

if __name__ == "__main__":
    solve()