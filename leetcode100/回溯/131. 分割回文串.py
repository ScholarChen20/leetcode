"""
给你一个字符串 s，请你将 s 分割成一些 子串，使每个子串都是 回文串 。返回 s 所有可能的分割方案。
示例 1：

输入：s = "aab"
输出：[["a","a","b"],["aa","b"]]
示例 2：

输入：s = "a"
输出：[["a"]]
"""
from typing import List
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        """
        思路：回溯
        1. 从 s 中选择一个字符，加入到 path 中，然后递归调用 facktrace 函数，start 保持不变
        2. 递归调用 facktrace 函数，start 保持不变
        """
        n = len(s)
        res = []
        def facktrace(path, start):
            if start == n:
                res.append(path[:])
                return
            for i in range(start, n):
                if s[start:i+1] == s[start:i+1][::-1]:
                    path.append(s[start:i+1])
                    facktrace(path, i + 1)
                    path.pop()
        facktrace([], 0)
        return res

if __name__ == '__main__':
    s = Solution()
    # print(s.partition("aab"))
    print(s.partition("abbf"))