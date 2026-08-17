"""
给你一个未排序的整数数组 nums ，请你找出其中没有出现的最小的正整数。
请你实现时间复杂度为 O(n) 并且只使用常数级别额外空间的解决方案
示例 1：

输入：nums = [1,2,0]
输出：3
解释：范围 [1,2] 中的数字都在数组中。
"""
from typing import List


class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        """
        原地哈希，将数字放到对应的位置上，然后遍历数组，找到第一个不在对应位置上的数字
        时间复杂度O(n)，空间复杂度O(1)

        """
        n = len(nums)
        for i in range(n):
            while 1 <= nums[i] <= n and nums[i] != nums[nums[i] - 1]:
                nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1] # 交换（保证每个数字都放在对应的位置上，不在则交换位置）
        for i in range(n):
            if nums[i] != i + 1:
                return i + 1
        return n + 1

if __name__ == '__main__':
    nums = [1,3,2]
    print(Solution().firstMissingPositive(nums))