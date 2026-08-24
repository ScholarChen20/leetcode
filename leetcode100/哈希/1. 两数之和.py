"""
给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出 和为目标值 target  的那 两个 整数，并返回它们的数组下标。
你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。
你可以按任意顺序返回答案。

示例 1：
输入：nums = [2,7,11,15], target = 9
输出：[0,1]               解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。
示例 2：

输入：nums = [3,2,4], target = 6
输出：[1,2]

示例 3：
输入：nums = [3,3], target = 6
输出：[0,1]
"""
from typing import List
class Solution:
    def twoSum(self, nums: List[int], target: int):
        """使用哈希表，时间复杂度O(n)，空间复杂度O(n)"""
        hashmap = {}
        for i, num in enumerate(nums):
            if target - num in hashmap:
                return [hashmap[target - num], i]
            hashmap[num] = i
        return []

    def twoSum1(self, nums: List[int], target: int):
        """暴力解法，时间复杂度O(n**2)，空间复杂度O(1)"""
        n = len(nums)
        for i in range(n):
            for j in range(i+1, n):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []

    def twoSum2(self, nums: List[int], target: int):
        """排序+双指针，时间复杂度O(nlogn)，空间复杂度O(n)"""
        n = len(nums)
        sorted_nums = sorted(enumerate(nums), key=lambda x: x[1])
        left, right = 0, n - 1
        while left < right:
            sum = sorted_nums[left][1] + sorted_nums[right][1]
            if sum == target:
                return [sorted_nums[left][0], sorted_nums[right][0]]
            elif sum < target:
                left += 1
            else:
                right -= 1
        return []

if __name__ == '__main__':
    s = Solution()
    # print(s.twoSum([2, 7, 11, 15], 9))
    print(s.twoSum1([3, 2, 4], 6))
