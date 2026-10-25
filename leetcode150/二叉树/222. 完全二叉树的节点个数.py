"""
给你一棵 完全二叉树 的根节点 root ，求出该树的节点个数。
完全二叉树 的定义如下：在完全二叉树中，除了最底层节点可能没填满外，其余每层节点数都达到最大值，并且最下面一层的节点都集中在该层最左边的若干位置。若最底层为第 h 层（从第 0 层开始），则该层包含 1~ 2h 个节点。

示例 1：
输入：root = [1,2,3,4,5,6]
输出：6

示例 2：
输入：root = []
输出：0

示例 3：
输入：root = [1]
输出：1
"""
from typing import Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def countNodes(self, root: Optional[TreeNode]) -> int: # 递归法
        if not root:
            return 0
        return 1 + self.countNodes(root.left) + self.countNodes(root.right)

    def countNodes2(self, root: Optional[TreeNode]) -> int: # 迭代法
        if not root:
            return 0
        queue = [root]
        count = 0
        while queue:
            node = queue.pop()
            count += 1
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return count


class Solution1:
    def height(self, root: TreeNode): # 求二叉树的深度
        height = 0
        while root:
            root = root.left
            height += 1

        return height

    def countNodes(self, root: TreeNode) -> int: # 空树，节点数为 0
        if root == None: # 求左子树和右子树的深度
            return 0
        leftHeight = self.height(root.left)
        rightHeight = self.height(root.right)

        if leftHeight == rightHeight: # 如果左子树的深度 = 右子树的深度，左子树为满二叉树
            return (2 ** leftHeight - 1) + self.countNodes(root.right) + 1 # 节点数 = 左子树的深度 + 右子树的深度 + 根节点

        else: # 如果左子树的深度 ＞ 右子树的深度，右子树为满二叉树
            return (2 ** rightHeight - 1) + self.countNodes(root.left) + 1 # 节点数 = 左子树的深度 + 右子树的深度 + 根节点

if __name__ == '__main__':
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    root.right.left = TreeNode(6)
    print(Solution().countNodes(root))
