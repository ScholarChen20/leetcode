"""
53. 最大子数组和
给你一个整数数组 nums ，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。
子数组是数组中的一个连续部分。

示例 1：

输入：nums = [-2,1,-3,4,-1,2,1,-5,4]
输出：6
解释：连续子数组 [4,-1,2,1] 的和最大，为 6 。
"""

class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        """
        动态规划
        :param nums:
        :return:
        """
        n = len(nums)
        dp = [0] * n
        dp[0] = nums[0]
        for i in range(1, n):
            dp[i] = max(dp[i - 1] + nums[i], nums[i])
        return max(dp)

    def maxSubArray2(self, nums: list[int]) -> int:
        """
        贪心算法, 当前元素和前一个元素的和比较大，则当前元素和前一个元素的和，否则当前元素和前一个元素的和为0
        :param nums:
        :return:
        """
        max_sum = nums[0]
        current_sum = nums[0]
        for i in range(1, len(nums)):
            current_sum = max(current_sum + nums[i], nums[i])
            max_sum = max(max_sum, current_sum)
        return max_sum

if __name__ == '__main__':
    s = Solution()
    nums = list(map(int, input().split()))
    print(s.maxSubArray(nums))