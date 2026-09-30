"""
给定一个含有 n 个正整数的数组和一个正整数 target 。

找出该数组中满足其和 ≥ target 的长度最小的 连续子数组 [numsl, numsl+1, ..., numsr-1, numsr] ，并返回其长度。如果不存在符合条件的子数组，返回 0 。

示例 1：
输入：target = 7, nums = [2,3,1,2,4,3]
输出：2
解释：子数组 [4,3] 是该条件下的长度最小的子数组。
"""
from typing import List
class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        left = right = 0
        sum = 0
        min_len = float('inf')
        while right < len(nums):
            sum += nums[right]
            while sum >= target:
                min_len = min(min_len, right - left + 1)
                sum -= nums[left]
                left += 1
            right += 1
        return min_len if min_len != float('inf') else 0

if __name__ == '__main__':
    m = Solution()
    print(m.minSubArrayLen(target=7, nums=[2,3,1,2,4,3]))