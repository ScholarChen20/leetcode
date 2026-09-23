"""
给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。
岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。
此外，你可以假设该网格的四条边均被水包围。
示例 1：

输入：grid = [
  ['1','1','1','1','0'],
  ['1','1','0','1','0'],
  ['1','1','0','0','0'],
  ['0','0','0','0','0']
]
输出：1
"""
from typing import List
class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        """DFS:从首节点开始往后遍历"""
        if not grid: return 0
        row = len(grid)
        col = len(grid[0])
        cnt = 0

        def dfs(i, j):
            if i<0 or i>=row or j<0 or j>=col or grid[i][j] == '0':
                return
            grid[i][j] = '0'
            dfs(i+1, j)
            dfs(i-1, j)
            dfs(i, j+1)
            dfs(i, j-1)

        for i in range(row):
            for j in range(col):
                if grid[i][j] == '1':
                    cnt += 1
                    dfs(i, j)
        return cnt

    def numIslands2(self, grid: List[List[str]]) -> int:
        """bfs: """
        if not grid: return 0
        row = len(grid)
        col = len(grid[0])
        cnt = 0
        for i in range(row):
            for j in range(col):
                if grid[i][j] == '1':
                    cnt += 1
                    stack = [(i, j)]
                    while stack:
                        x, y = stack.pop()
                        if 0 <= x < row and 0 <= y < col and grid[x][y] == '1':
                            grid[x][y] = '0'
                            stack.append((x + 1, y))
                            stack.append((x - 1, y))
                            stack.append((x, y + 1))
                            stack.append((x, y - 1))
        return cnt
if __name__ == '__main__':
    solution = Solution()
    grid = [
  ['1','1','1','1','0'],
  ['1','1','0','1','0'],
  ['1','1','0','0','0'],
  ['0','0','0','0','0']
]
    # print(solution.numIslands(grid))
    print(solution.numIslands2(grid))
