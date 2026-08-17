"""
给定两个字符串 s 和 t，长度分别是 m 和 n，返回 s 中的 最短窗口 子串，使得该子串包含 t 中的每一个字符（包括重复字符）。如果没有这样的子串，返回空字符串 ""。
测试用例保证答案唯一。
示例 1：

输入：s = "ADOBECODEBANC", t = "ABC"
输出："BANC"
解释：最小覆盖子串 "BANC" 包含来自字符串 t 的 'A'、'B' 和 'C'。
示例 2：

输入：s = "a", t = "a"
输出："a"
解释：整个字符串 s 是最小覆盖子串。
"""
from collections import Counter

"""具体来说：
1.初始化 ansLeft=−1, ansRight=m，用来记录最短子串的左右端点，其中 m 是 s 的长度。
2.用一个哈希表（或者数组）cntT 统计 t 中每个字母的出现次数。
3.初始化 left=0，以及一个空哈希表（或者数组）cntS，用来统计 s 子串中每个字母的出现次数。
4.历 s，设当前枚举的子串右端点为 right，把 s[right] 的出现次数加一。
5.遍历 cntS 中的每个字母及其出现次数，如果出现次数都大于等于 cntT 中的字母出现次数：
 如果 right−left<ansRight−ansLeft，说明我们找到了更短的子串，更新 ansLeft=left, ansRight=right。
 把 s[left] 的出现次数减一。
 左端点右移，即 left 加一。
 重复上述三步，直到 cntS 有字母的出现次数小于 cntT 中该字母的出现次数为止。
最后，如果 ansLeft<0，说明没有找到符合要求的子串，返回空字符串，否则返回下标 ansLeft 到下标 ansRight 之间的子串。
"""
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        cnt_s = Counter()
        cnt_t = Counter(t)
        ans_left , ans_rigth = -1, len(s)
        left = 0

        for right,c in enumerate(s):
            cnt_s[c] += 1
            while cnt_s >= cnt_t:
                if right - left < ans_rigth - ans_left:
                    ans_left, ans_rigth = left, right
                cnt_s[s[left]] -= 1
                left += 1

        return "" if ans_left < 0 else s[ans_left:ans_rigth + 1]

if __name__ == '__main__':
    s = Solution()
    print(s.minWindow("ADOBECODEBANC", "ABC"))