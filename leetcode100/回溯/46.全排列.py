"""
给定一个不含重复数字的数组 nums ，返回其 所有可能的全排列 。
你可以 按任意顺序 返回答案。

示例：
输入：nums = [1,2,3]
输出：[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
"""

from typing import List
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        """回溯 + 剪枝: used 数组记录每个数字是否被使用过，如果被使用过，则跳过，否则添加到 path 中，然后递归，最后回溯"""
        n = len(nums)
        used = [False] * n
        res = []
        def facktrack(path, used):
            if len(path) == n:
                res.append(path[:])
                return
            for i in range(n):
                if used[i]:
                    continue
                path.append(nums[i])
                used[i] = True
                facktrack(path, used)
                path.pop()
                used[i] = False

        facktrack([], used)
        return res

if __name__ == '__main__':
    s = Solution()
    # print(s.permute([1,2,3]))
    # print(s.permute([1,3]))
    print(s.permute([1]))