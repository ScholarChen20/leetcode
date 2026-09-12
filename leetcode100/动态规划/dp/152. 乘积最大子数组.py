"""
给你一个整数数组 nums ，请你找出数组中乘积最大的非空连续 子数组（该子数组中至少包含一个数字），并返回该子数组所对应的乘积。
测试用例的答案是一个 32-位 整数。
请注意，一个只包含一个元素的数组的乘积是这个元素的值。
示例 1:
输入: nums = [2,3,-2,4]
输出: 6
解释: 子数组 [2,3] 有最大乘积 6。
示例 2:
输入: nums = [-2,0,-1]
输出: 0
解释: 结果不能为 2, 因为 [-2,-1] 不是子数组。
"""
from typing import List
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        """
        二维dp， dp[i][0]表示以nums[i]结尾的最小乘积，dp[i][1]表示以nums[i]结尾的最大乘积
        时间复杂度：O(n)
        空间复杂度：O(n)
        """
        n = len(nums)
        dp = [[0] * 2 for _ in range(n)]
        dp[0][0] = nums[0]
        dp[0][1] = nums[0]
        ans = nums[0]
        for i in range(1,n):
            dp[i][0] = min(dp[i-1][0] * nums[i], dp[i-1][1] * nums[i], nums[i])
            dp[i][1] = max(dp[i-1][0] * nums[i], dp[i-1][1] * nums[i], nums[i])
            ans = max(ans, dp[i][1])
            # print(dp)
        return ans
if __name__ == '__main__':
    # print(Solution().maxProduct([-2,3,-4]))
    print(Solution().maxProduct([-2,0,-1]))