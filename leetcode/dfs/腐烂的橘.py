"""
腐烂的橘子
在给定的 m x n 网格 grid 中，每个单元格可以有以下三个值之一：

值 0 代表空单元格；
值 1 代表新鲜橘子；
值 2 代表腐烂的橘子。
每分钟，腐烂的橘子 周围 4 个方向上相邻 的新鲜橘子都会腐烂。

返回 直到单元格中没有新鲜橘子为止所必须经过的最小分钟数。如果不可能，返回 -1 。

输入：grid = [[2,1,1],[1,1,0],[0,1,1]]
输出：4
"""
from typing import List
from collections import deque

class solution():
    def orangeRotting(self,grid: List[List[int]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        queue = deque()
        fresh_count = 0

        # 找出所有腐烂橘子和新鲜橘子数量
        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == 2:
                    queue.append((i, j, 0))
                elif grid[i][j] == 1:
                    fresh_count += 1

        # 如果没有腐烂的橘子直接返回
        if fresh_count == 0:
            return 0

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        max_time = 0
        while queue:
            r,c,time = queue.popleft()
            max_time = max(max_time, time)
            for dr,dc in directions:
                nr,nc = r+dr,c+dc
                if 0<=nr<rows and 0<=nc<cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh_count -= 1
                    queue.append((nr,nc,time+1))

        return max_time if fresh_count > 0 else 0

import sys
if __name__ == '__main__':
    input = sys.stdin.read()
    """
    输入：[[2,1,1],[1,1,0],[0,1,1]]
    """
    # 读取所有输入
    input_lines = sys.stdin.read().split()
    if not input_lines:
        sys.exit(0)

    # 解析行数和列数
    m = int(input_lines[0])
    n = int(input_lines[1])
    print(m,n)

    grid = []
    index = 2
    for i in range(m):
        row = []
        for j in range(n):
            row.append(int(input_lines[index]))
            index += 1
        grid.append(row)

    print(solution().orangeRotting(grid))
