"""
给定两个整数 n 和 k，返回范围 [1, n] 中所有可能的 k 个数的组合。
你可以按 任何顺序 返回答案。

示例 1：
输入：n = 4, k = 2
输出：
[
  [2,4],
  [3,4],
  [2,3],
  [1,2],
  [1,3],
  [1,4],
]
"""
class Solution:
    def combine(self, n: int, k: int) :
        res = []
        def backtrace(path, start):
            if len(path) == k:
                res.append(path[:])
                return
            for i in range(start, n + 1):
                path.append(i)
                backtrace(path, i + 1)
                path.pop()

        backtrace([], 1)
        return res

if __name__ == '__main__':
    s = Solution()
    print(s.combine(4, 2))