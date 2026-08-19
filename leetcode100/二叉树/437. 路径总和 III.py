"""
给定一个二叉树的根节点 root ，和一个整数 targetSum ，求该二叉树里节点值之和等于 targetSum 的 路径 的数目。
路径 不需要从根节点开始，也不需要在叶子节点结束，但是路径方向必须是向下的（只能从父节点到子节点）。

示例 1：
输入：root = [10,5,-3,3,2,null,11,3,-2,null,1], targetSum = 8
输出：3
解释：和等于 8 的路径有 3 条，如图所示。
示例 2：

输入：root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
输出：3
"""
import collections
from typing import Optional
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        """递归实现，首先定义rootSum(p,val) 表示以节点 p 为起点向下且满足路径总和为 val 的路径数目
        采用递归遍历二叉树的每个节点 p，对节点 p 求 rootSum(p,val)，然后将每个节点所有求的值进行相加求和返回。"""
        if not root:
             return 0
        def dfs(root, targetSum):
            if not root:
                return 0
            res = 0
            if root.val == targetSum:
                res += 1
            res += dfs(root.left, targetSum - root.val)
            res += dfs(root.right, targetSum - root.val)
            return res
        return dfs(root, targetSum) + self.pathSum(root.left, targetSum) + self.pathSum(root.right, targetSum)

    def pathSum1(self, root: TreeNode, targetSum: int) -> int:
        """前缀和+哈希表：前缀和：记录从根节点到当前节点的路径和，哈希表：记录前缀和出现的次数
        cur:记录从根节点到当前节点的路径和 prefix:记录前缀和出现的次数 prefix[cur - targetSum]：记录前缀和出现的次数"""
        prefix = collections.defaultdict(int)
        prefix[0] = 1

        def dfs(root, cur):
            if not root:
                return 0
            cur += root.val # 记录从根节点到当前节点的路径和
            res = prefix[cur - targetSum] # 记录前缀和出现的次数
            prefix[cur] += 1 # 前缀和出现的次数加1
            res += dfs(root.left, cur) # 递归左子树
            res += dfs(root.right, cur) # 递归右子树
            prefix[cur] -= 1 # 前缀和出现的次数减1
            return res

        return dfs(root, 0)



if __name__ == '__main__':
    root = TreeNode(10)
    root.left = TreeNode(5)
    root.right = TreeNode(-3)
    root.left.left = TreeNode(3)
    root.left.right = TreeNode(2)
    root.right.right = TreeNode(11)
    root.left.left.left = TreeNode(3)
    root.left.left.right = TreeNode(-2)
    root.left.right.right = TreeNode(1)
    print(Solution().pathSum1(root, 15))
