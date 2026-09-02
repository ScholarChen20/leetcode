"""
给定一个数组 prices ，它的第 i 个元素 prices[i] 表示一支给定股票第 i 天的价格。
你只能选择 某一天 买入这只股票，并选择在 未来的某一个不同的日子 卖出该股票。设计一个算法来计算你所能获取的最大利润。
返回你可以从这笔交易中获取的最大利润。如果你不能获取任何利润，返回 0 。

示例 1：

输入：[7,1,5,3,6,4]
输出：5
解释：在第 2 天（股票价格 = 1）的时候买入，在第 5 天（股票价格 = 6）的时候卖出，最大利润 = 6-1 = 5 。
     注意利润不能是 7-1 = 6, 因为卖出价格需要大于买入价格；同时，你不能在买入前卖出股票。
"""
from cmath import inf
from typing import List
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """
        贪心思路：遍历数组，记录最大利润，再记录最小价格
        时间复杂度：O(n)
        空间复杂度：O(1)
        """
        min_num = inf # 无穷大
        max_price =0
        for price in prices:
            max_price = max(price - min_num, max_price)
            min_num = min(price, min_num)
        return max_price


if __name__ == '__main__':
    s=Solution()
    print(s.maxProfit([7,1,5,3,6,4]))
    print(s.maxProfit([7,6,4,3,1]))