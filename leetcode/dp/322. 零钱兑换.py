"""
给你一个整数数组 coins ，表示不同面额的硬币；以及一个整数 amount ，表示总金额。

计算并返回可以凑成总金额所需的 最少的硬币个数 。如果没有任何一种硬币组合能组成总金额，返回 -1 。

你可以认为每种硬币的数量是无限的。



示例 1：

输入：coins = [1, 2, 5], amount = 11
输出：3
解释：11 = 5 + 5 + 1
示例 2：

输入：coins = [2], amount = 3
输出：-1
示例 3：

输入：coins = [1], amount = 0
输出：0
"""
from cmath import inf
from functools import cache
from typing import List




class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        n= len(coins)
        coins.sort()
        def dfs(i, j, coinsList):
            if j == 0 and i >= 0:
                return 0
            if j < 0 or i < 0:
                return inf
            if j >= coinsList[i] and i >= 0:
                return min(dfs(i - 1, j-coinsList[i], coinsList) + 1 , dfs(i, j - coinsList[i], coinsList) + 1)
            else:
                return dfs(i - 1, j, coinsList)

        ans = dfs(n-1, amount, coins)
        return ans if ans != inf else -1

if __name__ == '__main__':
    print(Solution().coinChange([2,5,10,1], 27))