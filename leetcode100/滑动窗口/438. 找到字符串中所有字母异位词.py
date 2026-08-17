"""
给定两个字符串 s 和 p，找到 s 中所有 p 的 异位词 的子串，返回这些子串的起始索引。不考虑答案输出的顺序。
示例 1:

输入: s = "cbaebabacd", p = "abc"
输出: [0,6]
解释:
起始索引等于 0 的子串是 "cba", 它是 "abc" 的异位词。
起始索引等于 6 的子串是 "bac", 它是 "abc" 的异位词。
"""
from collections import defaultdict
from typing import List


class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:

        n = len(s)
        k = len(p)

        if n < k:
            return []

        # 统计 p 的字符频率
        p_count = defaultdict(int)
        for char in p:
            p_count[char] += 1

        # 初始化滑动窗口的字符频率
        window_count = defaultdict(int)
        for i in range(k):
            window_count[s[i]] += 1

        res = []
        if window_count == p_count:
            res.append(0)

        for i in range(k, n):
            # 移除左边界字符
            left_char= s[i - k]
            window_count[left_char] -= 1  # 移除旧字符
            if window_count[left_char] == 0:
                del window_count[left_char]  # 删除频率为0的字符

            # 添加有边界字符
            right_char = s[i]
            window_count[right_char] += 1  # 添加新字符


            if window_count == p_count:
                res.append(i - k + 1)

        return res

if __name__ == '__main__':
    s = Solution()
    str1 = "cbaebabacd"
    str2 = "abc"
    print(s.findAnagrams(str1, str2))