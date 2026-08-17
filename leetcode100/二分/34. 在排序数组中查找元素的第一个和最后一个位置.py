"""
给你一个按照非递减顺序排列的整数数组 nums，和一个目标值 target。请你找出给定目标值在数组中的开始位置和结束位置。
如果数组中不存在目标值 target，返回 [-1, -1]。
你必须设计并实现时间复杂度为 O(log n) 的算法解决此问题。
示例 1：

输入：nums = [5,7,7,8,8,10], target = 8
输出：[3,4]
示例 2：

输入：nums = [5,7,7,8,8,10], target = 6
输出：[-1,-1]
示例 3：

输入：nums = [], target = 0
输出：[-1,-1]
"""
from typing import List


class Solution:
    def searchRange(self, nums: List[int], target: int):
        n = len(nums)
        ans = [-1, -1]
        if n == 0:
            return ans
        left = 0
        right = n - 1

        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                left = mid + 1
            else:
                right = mid
        if nums[left] != target:
            return ans
        ans[0] = left

        right = n - 1
        while left < right:
            mid = (left + right + 1) // 2
            if nums[mid] > target:
                right = mid - 1
            else:
                left = mid
        if nums[right] != target:
            return ans
        ans[1] = right
        return ans

if __name__ == '__main__':
    print(Solution().searchRange([5,7,7,8,8,10], 8))
    # print(Solution().searchRange([1], 1))

