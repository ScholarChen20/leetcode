"""
给定一个字符串 s，将 s 分割成一些子串，使每个子串都是回文串。
返回 s 所有可能的分割方案。

示例:

输入: "aab"
输出:
[
  ["aa","b"],
  ["a","a","b"]
]
"""
class Solution:
    def partition(self, s: str):
        n = len(s)
        res = []
        def backtrace(path, start):
            if start == n:
                res.append(path[:])
                return
            for i in range(start, n):
                if s[start : i + 1] == s[start : i + 1][::-1]:
                    path.append(s[start : i + 1])
                    backtrace(path, i + 1)
                    path.pop()

        backtrace([], 0)
        return res
if __name__ == '__main__':
    s = Solution()
    # print(s.partition("aab"))
    s = "aba"
    print(s[0:2])
    print(s[1:3])
