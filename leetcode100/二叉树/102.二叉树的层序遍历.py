"""
给定一个二叉树，返回其按层次遍历的节点值。 （即逐层地，从左到右访问所有节点）。

例如:
给定二叉树: [3,9,20,null,null,15,7],

    3
   / \
  9  20
    /  \
   15   7
返回其层次遍历结果：

[
  [3],
  [9,20],
  [15,7]
]
"""
from typing import List, Optional
class TreeNode:
    def __init__(self, val =0 , left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        """迭代实现,队列实现 BFS """
        res = []
        queue = [root]
        while queue:
            level = []
            for _ in range(len(queue)):
                node = queue.pop(0)
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            res.append(level)
        return res

    def levelOrder2(self, root: Optional[TreeNode]) -> List[List[int]]:
        """递归实现, DFS ,前序遍历, 每次递归时，将当前节点的值添加到res的对应位置"""
        res = []
        def helper(node, level):
            if not node:
                return
            if len(res) == level: # 如果res的长度等于层数，说明res中没有这一层的节点，需要添加一个空列表
                res.append([])
            res[level].append(node.val)
            helper(node.left, level + 1)
            helper(node.right, level + 1)
        helper(root, 0)
        return res

if __name__ == '__main__':
    root = TreeNode(3)
    root.left = TreeNode(9)
    root.right = TreeNode(20)
    root.right.left = TreeNode(15)
    root.right.right = TreeNode(7)
    print(Solution().levelOrder(root))
    print(Solution().levelOrder2(root))