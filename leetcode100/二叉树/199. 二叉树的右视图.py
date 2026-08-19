"""
给定一个二叉树的 根节点 root，想象自己站在它的右侧，按照从顶部到底部的顺序，返回从右侧所能看到的节点值。
示例 1：
输入：root = [1,2,3,null,5,null,4]
输出：[1,3,4]

示例 2：
输入：root = [1,2,3,4,null,null,null,5]
输出：[1,3,4,5]

示例 3：
输入：root = [1,null,3]
输出：[1,3]
"""
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        """层序遍历，每次取每层的最后一个节点"""
        if not root:
            return []
        res = []
        queue = [root] # 队列,队列中存储的是每层的节点
        while queue:
            size = len(queue)
            for i in range(size):
                cur = queue.pop(0)
                if i == size - 1:
                    res.append(cur.val)
                if cur.left:
                    queue.append(cur.left)
                if cur.right:
                    queue.append(cur.right)
        return res
if __name__ == '__main__':
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.right = TreeNode(5)
    root.right.right = TreeNode(4)
    print(Solution().rightSideView(root))


