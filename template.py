import sys
from typing import List

input = sys.stdin.readline


class Solution:
    def solve(self, arr):
        """核心逻辑函数，与输入输出解耦"""
        # 实现算法逻辑 todo
        result = 0
        return result

class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        sum=0
        m=len(grid)
        n=len(grid[0])

        def dfs(grid: List[List[str]], i: int, j: int) -> None:
            if i < 0 or i >= m or j < 0 or j >= n:
                return
            if grid[i][j] == "1":
                dfs(grid,i-1,j)
                dfs(grid,i,j-1)
                dfs(grid,i,j+1)
                dfs(grid,i+1,j)

        for i in range(m):
            for j in range(n):
                if grid[i][j] == '1':
                    sum+=1
                    dfs(grid,i,j)

        return sum

if __name__ == "__main__":
    sol = Solution()
    # 处理输入
    n = int(input())
    arr = list(map(int, input().split()))
    # 调用解法并输出
    print(sol.solve(arr))