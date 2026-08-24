"""
给定两个字符串 s 和 p，找到 s 中所有 p 的 异位词 的子串，返回这些子串的起始索引。不考虑答案输出的顺序。
示例 1:
输入: s = "cbaebabacd", p = "abc"
输出: [0,6]     (解释:起始索引等于 0 的子串是 "cba", 它是 "abc" 的异位词。起始索引等于 6 的子串是 "bac", 它是 "abc" 的异位词。)

示例 2:
输入: s = "abab", p = "ab"
输出: [0,1,2]
"""
from collections import defaultdict, Counter
from typing import List
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        n, k= len(s), len(p)
        if n < k:
            return []

        p_count = Counter(p)  # 统计 p 的字符频率
        window_count = defaultdict(int) # 初始化滑动窗口的字符频率
        for i in range(k):
            window_count[s[i]] += 1

        res = []
        if window_count == p_count:
            res.append(0)

        for i in range(k, n): # 滑动窗口
            left_char= s[i - k] # 移除左边界字符
            window_count[left_char] -= 1  # 移除旧字符
            if window_count[left_char] == 0:
                del window_count[left_char]  # 删除频率为0的字符
            # 添加有边界字符
            right_char = s[i]
            window_count[right_char] += 1  # 添加新字符
            # 判断是否是异位词
            if window_count == p_count:
                res.append(i - k + 1)
        return res

    def findAnagrams2(self, s: str, p: str) -> List[int]:
        """滑动窗口，时间复杂度O(n)，空间复杂度O(n)"""
        n ,t = len(s), len(p)
        if n < t:
            return []
        res = []
        p_count = [0] * 26 # 26个字母
        window_count = [0] * 26
        for i in range(t):
            p_count[ord(p[i]) - ord('a')] += 1
            window_count[ord(s[i]) - ord('a')] += 1
        if window_count == p_count:
            res.append(0)

        for i in range(t,n):
            # 移除左边界字符
            p_count[ord(s[i - t]) - ord('a')] -= 1
            # 添加右边界字符
            p_count[ord(s[i]) - ord('a')] += 1
            if window_count == p_count:
                res.append(i - t + 1)

        return res

if __name__ == '__main__':
    s = Solution()
    str1 = "cbaebabacd"
    str2 = "abc"
    print(s.findAnagrams2(str1, str2))
    # print(s.findAnagrams2("abab", "ab"))