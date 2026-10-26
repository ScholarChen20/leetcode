"""
给你一个整数数组 nums ，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。
子数组是数组中的一个连续部分。

示例 1：
输入：nums = [-2,1,-3,4,-1,2,1,-5,4]
输出：6
解释：连续子数组 [4,-1,2,1] 的和最大，为 6 。

示例 2：
输入：nums = [1]
输出：1

示例 3：
输入：nums = [5,4,-1,7,8]
输出：23
"""
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        max_len = 0
        n = len(nums)
        dp = [0] * n # dp[i]表示以nums[i]结尾的最大连续子数组最大值
        dp[0] = nums[0]
        for i in range(1, n):
            dp[i] = max(nums[i], dp[i-1] + nums[i])

        return max(dp)

    def maxSubArray2(self, nums: list[int]) -> int:
        current_num = nums[0]
        max_num = nums[0]
        for num in nums:
            current_num = max(current_num, current_num + num)
            max_num = max(current_num, max_num)

        return max_num

if __name__ == '__main__':
    s = Solution()
    print(s.maxSubArray([5,4,-1,7,8]))