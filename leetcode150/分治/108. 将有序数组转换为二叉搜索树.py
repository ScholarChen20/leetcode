"""
给你一个整数数组 nums ，其中元素已经按 升序 排列，请你将其转换为一棵 高度平衡 二叉搜索树。
示例1：
输入：nums = [-10,-3,0,5,9]
输出：[0,-10,5,-3,null,9]

示例2：
输入：nums = [1,3]
输出：[3,1]

"""
from typing import List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> TreeNode:
        if not nums:
            return None
        mid = len(nums) // 2
        root = TreeNode(nums[mid])
        root.left = self.sortedArrayToBST(nums[:mid])
        root.right = self.sortedArrayToBST(nums[mid+1:])
        return root

if __name__ == '__main__':
    s = Solution()
    root = s.sortedArrayToBST([-10,-3,0,5,9])
    while root:
        print(root.val)
        root = root.left

    # print(s.sortedArrayToBST([1,3]))