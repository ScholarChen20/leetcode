"""
给你二叉树的根结点 root ，请你将它展开为一个单链表：
展开后的单链表应该同样使用 TreeNode ，其中 right 子指针指向链表中下一个结点，而左子指针始终为 null 。
展开后的单链表应该与二叉树 先序遍历 顺序相同。

示例 1：
输入：root = [1,2,5,3,4,null,6]
输出：[1,null,2,null,3,null,4,null,5,null,6]
示例 2：

输入：root = []
输出：[]
示例 3：

输入：root = [0]
输出：[0]
"""
from typing import Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        """递归实现，先将左右子树展开，然后将右子树接到左子树的右子树上，然后将左子树接到右子树上"""
        if not root:
            return
        self.flatten(root.left) # 先将左右子树展开
        self.flatten(root.right) # 再将右子树展开
        # 将左子树接到右子树上
        left = root.left
        right = root.right
        root.left = None
        root.right = left
        cur = root
        # 将右子树接到左子树的右子树上
        while cur.right:
            cur = cur.right
        cur.right = right
        return root

    def flatten2(self, root: Optional[TreeNode]) -> None:
        """迭代实现，先将左右子树展开，然后将右子树接到左子树的右子树上，然后将左子树接到右子树上"""
        if not root:
            return None
        stack = [root]
        while stack:
            cur = stack.pop()
            if cur.right:
                stack.append(cur.right)
            if cur.left:
                stack.append(cur.left)
            if stack:
                cur.right = stack[-1]
            cur.left = None
        return root

if __name__ == '__main__':
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(5)
    root.left.left = TreeNode(3)
    root.left.right = TreeNode(4)
    root.right.right = TreeNode(6)
    # 输出所有元素
    print(Solution().flatten(root))
    print(Solution().flatten2(root))