"""
给定一个不含重复数字的数组 nums ，返回其 所有可能的全排列 。
你可以 按任意顺序 返回答案。

示例：
输入：nums = [1,2,3]
输出：[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
"""
from typing import List
class Solution:
    def permuete(self, nums: List[int]):
        n = len(nums)
        res = []
        used = [False] * n # used 记录每个数字是否被使用过
        def backtrace(path, used):
            if len(path) == n:
                res.append(path[:])
                return
            for i in range(n):
                if used[i]:
                    continue
                path.append(nums[i])
                used[i] = True
                backtrace(path, used)
                path.pop()
                used[i] = False
        backtrace([], used)
        return res

if __name__ == '__main__':
    s = Solution()
    print(s.permuete([1,2,3]))
