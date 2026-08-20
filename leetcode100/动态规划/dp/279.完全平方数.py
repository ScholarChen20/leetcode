"""
给你一个整数 n ，返回 和为 n 的完全平方数的最少数量 。
完全平方数 是一个整数，其值等于另一个整数的平方；换句话说，其值等于一个整数自乘的积。例如，1、4、9 和 16 都是完全平方数，而 3 和 11 不是。
示例 1：
输入：n = 12
输出：3
解释：12 = 4 + 4 + 4
示例 2：
输入：n = 13
输出：2
解释：13 = 4 + 9
"""
from cmath import inf
from functools import cache


class Solution:
    def numSquares(self, n: int) -> int:
        f=int(pow(n,0.5))
        @cache
        def dfs(i,j):
            if i==0:
                return 0 if j==0 else inf
            if j>=i*i:
                return min(dfs(i-1,j),dfs(i,j-i*i)+1)
            else:
                return dfs(i-1,j)
        ans=dfs(f,n)
        dfs.cache_clear()
        return ans

    def numSquares2(self, n: int) -> int:
        """
        动态规划,dp[i]表示和为i的最少完全平方数个数
        """
        dp = [inf] * (n + 1) # 初始化dp表示dp[i]表示和为i的最少完全平方数个数
        dp[0] = 0
        for i in range(1, n+1):
            for j in range(1, i+1):
                if j*j <= i:
                    dp[i] = min(dp[i], dp[i - j*j] + 1)
        return dp[-1]


if __name__ == '__main__':
    # print(Solution().numSquares(214))
    print(Solution().numSquares2(13))
