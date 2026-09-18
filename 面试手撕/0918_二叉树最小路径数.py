"""
二叉树，查询从根节点到叶子结点的路径,有个目标值，求根节点到叶子节点上和为目标值的最小路径

示例：
root = [1,2, 3] , target = 3
输出：1
解释：最小路径和为 1 (1->2) 或 (1->3)

示例2：
root = [1,2,3,4,5], target = 7
输出：2
解释：最小路径和为 2 (1->2->4) 或 (1->3->5)
"""
from typing import List
class ListNode:
    def __init__ (self, val = 0, left = None, right = None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def minPathSum(self, root: ListNode, target: int) -> int:
        min_num = 0 # 最小路径数

        def dfs(root: ListNode, current_val: int, level: int):
            if not root:
                return 0
            current_val += root.val
            if not root.left and not root.right: # 到达叶子节点
                if current_val == target: #
                    nonlocal min_num
                    min_num = min(min_num, level) if min_num != 0 else level

            else:
                dfs(root.left, current_val, level + 1)
                dfs(root.right, current_val, level + 1)

            current_val -= root.val

        dfs(root, 0, 0)
        return min_num if min_num !=0 else -1

        # return min(res, key= lambda x: len(x))
if __name__ == '__main__':
    root = ListNode(1)
    root.left = ListNode(2)
    root.right = ListNode(3)
    root.left.left = ListNode(4)
    root.left.right = ListNode(5)

    solution = Solution()
    print(solution.minPathSum(root, 7))


