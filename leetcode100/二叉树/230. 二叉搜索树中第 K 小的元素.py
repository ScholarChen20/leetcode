"""
给定一个二叉搜索树的根节点 root ，和一个整数 k ，请你设计一个算法查找其中第 k 小的元素（k 从 1 开始计数）。
示例 1：


输入：root = [3,1,4,null,2], k = 1
输出：1
"""
from typing import Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        """递归实现 中序遍历：左根右, 先将左子树入栈，然后弹出栈顶元素，然后将右子树入栈"""
        res = []
        def inorder(root):
            if not root:
                return
            inorder(root.left)
            res.append(root.val)
            inorder(root.right)
            return res[k-1]
        return inorder(root)

    def kthSmallest2(self, root: Optional[TreeNode], k: int) -> int:
        """迭代实现 中序遍历：左根右, 先将左子树入栈，然后弹出栈顶元素，然后将右子树入栈"""
        res = []
        stack = []
        cur = root
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            res.append(cur.val)
            cur = cur.right
        return res[k-1]

if __name__ == '__main__':
    root = TreeNode(3)
    root.left = TreeNode(1)
    root.right = TreeNode(4)
    root.left.right = TreeNode(2)
    print(Solution().kthSmallest(root, 1))
    print(Solution().kthSmallest2(root, 1))