"""
给定两个整数数组 preorder 和 inorder ，其中 preorder 是二叉树的先序遍历， inorder 是同一棵树的中序遍历，请构造二叉树并返回其根节点。

示例 1:
输入: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
输出: [3,9,20,null,null,15,7]
示例 2:

输入: preorder = [-1], inorder = [-1]
输出: [-1]
"""
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        """递归实现，前序遍历的第一个节点是根节点，然后在中序遍历中找到根节点的位置，然后将中序遍历分为左右子树，然后递归构建左右子树"""
        if not preorder:
            return None
        root = TreeNode(preorder[0])
        root_index = inorder.index(preorder[0])
        root.left = self.buildTree(preorder[1:root_index + 1], inorder[:root_index])
        root.right = self.buildTree(preorder[root_index + 1:], inorder[root_index + 1:])
        return root

    def buildTree2(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        """迭代实现，前序遍历的第一个节点是根节点，然后在中序遍历中找到根节点的位置，然后将中序遍历分为左右子树，然后递归构建左右子树"""
        if not preorder:
            return None
        root = TreeNode(preorder[0])
        stack = [root]
        inorder_index = 0
        for i in range(1, len(preorder)):
            node = TreeNode(preorder[i])
            if node.val != inorder[inorder_index]:
                stack[-1].left = node
                stack.append(node)
            else:
                while stack and stack[-1].val == inorder[inorder_index]:
                    inorder_index += 1
                    node = stack.pop()
                node.right = node
                stack.append(node)
        return root

if __name__ == '__main__':
    preorder = [3,9,20,15,7]
    inorder = [9,3,15,20,7]
    print(Solution().buildTree(preorder, inorder))

