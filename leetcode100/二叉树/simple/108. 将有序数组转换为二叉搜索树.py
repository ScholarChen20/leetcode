"""
    题目描述:
        给你一个整数数组 nums ，其中元素已经按 升序 排列，请你将其转换为一棵 高度平衡 二叉搜索树。
        高度平衡 二叉树是一棵满足「每个节点的左右两个子树的高度差的绝对值不超过 1 」的二叉树。

    链接: https://leetcode-cn.com/problems/convert-sorted-array-to-binary-search-tree/

    示例：
    输入：nums = [-10,-3,0,5,9]
    输出：[0,-3,9,-10,null,5]

    输入：nums = [1,3]
    输出：[3,1]
"""
from typing import List, Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        """ 递归实现, 每次取数组中间的元素作为根节点，然后递归构建左右子树"""
        def buildTree(left, right):
            if left > right:
                return None
            mid = (left + right) // 2
            root = TreeNode(nums[mid])
            root.left = buildTree(left, mid - 1)
            root.right = buildTree(mid + 1, right)
            return root

        return buildTree(0, len(nums) - 1)