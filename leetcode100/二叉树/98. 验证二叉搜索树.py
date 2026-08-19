"""
给定一个二叉树，判断其是否是一个有效的二叉搜索树。

假设一个二叉搜索树具有如下特征：

节点的左子树只包含小于当前节点的数。
节点的右子树只包含大于当前节点的数。
所有左子树和右子树自身必须也是二叉搜索树。

示例：
输入:
    2
   / \
  1   3
输出: true
输入:
    5
   / \
  1   4
     / \
    3   6
输出: false
解释: 根节点的值为 5 ，但是其右子节点值为 4 。
"""
from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        """递归实现，判断左右子树是否满足二叉搜索树的定义"""
        if not root:
            return True
        def check(node, left, right):
            if not node:
                return True
            if not left < node.val < right:
                return False
            return check(node.left, left, node.val) and check(node.right, node.val, right)

        return check(root, float('-inf'), float('inf'))

if __name__ == '__main__':
    # root = TreeNode(2)
    # root.left = TreeNode(1)
    # root.right = TreeNode(3)

    root = TreeNode(5)
    root.left = TreeNode(1)
    root.right = TreeNode(4)
    root.right.left = TreeNode(3)
    root.right.right = TreeNode(6)
    print(Solution().isValidBST(root))

