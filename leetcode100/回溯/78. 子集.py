"""
给你一个整数数组 nums ，数组中的元素 互不相同 。返回该数组所有可能的子集（幂集）。
解集 不能 包含重复的子集。你可以按 任意顺序 返回解集。
示例 1：

输入：nums = [1,2,3]
输出：[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]
示例 2：

输入：nums = [0]
输出：[[],[0]]
"""
from typing import List
class Solution:
    def subsets(self, nums: List[int]):
        """
        思路：回溯
        """
        n = len(nums)
        res = []
        def facktrace(path, start):
            res.append(path[:])
            for i in range(start, n):
                path.append(nums[i])
                facktrace(path, i + 1)
                path.pop()
        facktrace([], 0)
        return res

if __name__ == '__main__':
    s = Solution()
    print(s.subsets([1,2,3]))