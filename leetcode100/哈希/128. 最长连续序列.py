"""
给定一个未排序的整数数组 nums ，找出数字连续的最长序列（不要求序列元素在原数组中连续）的长度。
请你设计并实现时间复杂度为 O(n) 的算法解决此问题。
示例 1：

输入：nums = [100,4,200,1,3,2]
输出：4
解释：最长数字连续序列是 [1, 2, 3, 4]。它的长度为 4。
示例 2：

输入：nums = [0,3,7,2,5,8,4,6,0,1]
输出：9
"""
from typing import List
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        """
        思路是：先将数组中的元素去重，然后遍历数组，如果当前元素-1不在数组中，说明当前元素是序列的起点，然后从当前元素开始向后遍历，直到当前元素+1不在数组中，说明当前元素是序列的终点，然后更新最长序列的长度
        """
        longest_stack = 0
        num_set = set(nums)
        for num in num_set:
            if num-1 not in num_set:
                current_num = num
                current_stack = 1

                while current_num+1 in num_set: # 当前元素+1在数组中，说明当前元素+1是序列的下一个元素
                    current_num += 1 # 当前元素+1
                    current_stack += 1

                longest_stack = max(longest_stack, current_stack) # 更新最长序列的长度
        return longest_stack

if __name__ == '__main__':
    s = Solution()
    nums = [100,4,200,1,3,2]
    nums2 = [0,3,7,2,5,8,4,6,0,1]
    print(s.longestConsecutive(nums2))