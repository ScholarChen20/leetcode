"""
给定一个二叉树，检查它是否是镜像对称的。

输入：root = [1,2,2,3,4,4,3]
输出：true
示例 2：

输入：root = [1,2,2,null,3,null,3]
输出：false
"""
from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        if not root:
            return True
        def check(left, right):
            if not left and not right:
                return True
            if not left or not right:
                return False
            return left.val == right.val and check(left.left, right.right) and check(left.right, right.left)
        return check(root.left, root.right)


if __name__ == '__main__':
     root = TreeNode(1)
     root.left = TreeNode(2)
     root.right = TreeNode(2)
     root.left.right = TreeNode(3)
     root.right.right = TreeNode(3)

     print(Solution().isSymmetric(root))