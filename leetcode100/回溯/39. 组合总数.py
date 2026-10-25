"""
给定一个无重复元素的数组 candidates 和一个目标数 target ，找出 candidates 中所有可以使数字和为 target 的组合。
candidates 中的数字可以无限制重复被选取。
说明：
所有数字（包括 target）都是正整数。
解集不能包含重复的组合。
示例 1：
输入：candidates = [2,3,6,7], target = 7,
所求解集为：
[
  [7],
  [2,2,3]
]
示例 2：
输入：candidates = [2,3,5], target = 8,
所求解集为：
[
  [2,2,2,2],
  [2,3,3],
  [3,5]
]
"""
from typing import List
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        """
        思路：回溯
        1. 从 candidates 中选择一个数，加入到 path 中，然后递归调用 facktrace 函数，target 减去这个数，start 保持不变
        2. 递归调用 facktrace 函数，target 减去这个数，start 保持不变
        """
        n = len(candidates)
        res = []
        def facktrace(path, start, target):
            if target == 0:  # 找到一个解
                res.append(path[:])
                return
            for i in range(start, n):
                if candidates[i] > target: # 剪枝
                    break
                path.append(candidates[i]) # 选择
                facktrace(path, i, target - candidates[i]) # 递归
                path.pop()
        facktrace([], 0, target)
        return res

if __name__ == '__main__':
    s = Solution()
    # print(s.combinationSum([2,3,6,7], 7))
    print(s.combinationSum([2,3,5], 8))