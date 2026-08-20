"""
给你一个整数数组 prices ，其中 prices[i] 表示某支股票第 i 天的价格。

在每一天，你可以决定是否购买和/或出售股票。你在任何时候 最多 只能持有 一股 股票。然而，你可以在 同一天 多次买卖该股票，但要确保你持有的股票不超过一股。
返回 你能获得的 最大 利润 。

示例 1：

输入：prices = [7,1,5,3,6,4]
输出：7
解释：在第 2 天（股票价格 = 1）的时候买入，在第 3 天（股票价格 = 5）的时候卖出, 这笔交易所能获得利润 = 5 - 1 = 4。
随后，在第 4 天（股票价格 = 3）的时候买入，在第 5 天（股票价格 = 6）的时候卖出, 这笔交易所能获得利润 = 6 - 3 = 3。
最大总利润为 4 + 3 = 7 。
"""
import sys
from typing import List
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """
        贪心算法，只要后一天比前一天大，就卖出，否则不买。原因是题目说可以一天多次买卖股票，所以只要后一天比前一天大，就卖出，否则不买。
        """
        profit = 0
        for i in range(1, len(prices)):
            if prices[i] > prices[i - 1]:
                profit += prices[i] - prices[i - 1]
        return profit

    def maxProfits(self, prices: List[int]) -> int:
        """
        动态规划，dp[i]表示前i天的最大利润，dp[i] = max(dp[i - 1], dp[i - 1] + prices[i] - prices[i - 1])
        """
        dp = [0] * len(prices)
        dp[0] = 0
        for i in range(1, len(prices)):
            dp[i] = max(dp[i-1], dp[i-1] + prices[i] - prices[i-1])
        return dp[-1]

if __name__ == '__main__':
    s=Solution()
    # print(s.maxProfit([7,1,5,3,6,4]))
    # print(s.maxProfit([1,2,3,4,5]))
    # print(s.maxProfit([7,6,4,3,1]))
    nums = list(map(int, input().strip().split()))
    # print(s.maxProfit(nums))
    print(s.maxProfits(nums))