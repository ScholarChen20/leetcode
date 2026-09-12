"""
给定一个包含非负整数的 m x n 网格 grid ，请找出一条从左上角到右下角的路径，使得路径上的数字总和为最小。

说明：每次只能向下或者向右移动一步。
输入：grid = [[1,3,1],[1,5,1],[4,2,1]]
输出：7
解释：因为路径 1→3→1→1→1 的总和最小。
示例 2：

输入：grid = [[1,2,3],[4,5,6]]
输出：12
"""
from typing import List
class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:
        """dp[i][j]表示从(0,0)到(i,j)的最小路径和 dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]"""
        dp = [[0] * len(grid[0]) for _ in range(len(grid))]
        # 初始顶行元素和第一列元素
        dp[0][0] = grid[0][0]
        for i in range(1, len(grid)):
            dp[i][0] = dp[i - 1][0] + grid[i][0]
        for j in range(1, len(grid[0])):
            dp[0][j] = dp[0][j - 1] + grid[0][j]

        for i in range(1, len(grid)):
            for j in range(1, len(grid[0])):
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1]) + grid[i][j]
        return dp[-1][-1]

if __name__ == '__main__':
    print(Solution().minPathSum([[1,2,3],[4,5,6]]))