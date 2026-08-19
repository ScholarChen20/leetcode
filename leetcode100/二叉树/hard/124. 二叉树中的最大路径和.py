"""
二叉树中的 路径 被定义为一条节点序列，序列中每对相邻节点之间都存在一条边。同一个节点在一条路径序列中 至多出现一次 。该路径 至少包含一个 节点，且不一定经过根节点。
路径和 是路径中各节点值的总和。
给你一个二叉树的根节点 root ，返回其 最大路径和 。


示例 1：
输入：root = [1,2,3]
输出：6

示例2：
输入：root = [-10,9,20,null,null,15,7]
输出：42
"""
from typing import Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        """递归实现"""
        self.max_sum = 0
        def dfs(root):
            if not root:
                return 0
            left = max(0, dfs(root.left))
            right = max(0, dfs(root.right))
            self.max_sum = max(self.max_sum, left + right + root.val)
            return max(left, right) + root.val
        dfs(root)
        return self.max_sum

if __name__ == '__main__':
    # root = TreeNode(1)
    # root.left = TreeNode(2)
    # root.right = TreeNode(3)
    # root.left.left = TreeNode(4)

    root = TreeNode(-10)
    root.left = TreeNode(9)
    root.right = TreeNode(20)
    root.right.left = TreeNode(15)
    root.right.right = TreeNode(7)

    print(Solution().maxPathSum(root))
