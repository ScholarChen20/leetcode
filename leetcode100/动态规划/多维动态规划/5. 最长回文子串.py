"""
给你一个字符串 s，找到 s 中最长的 回文 子串。
示例 1：

输入：s = "babad"
输出："bab"
解释："aba" 同样是符合题意的答案。
示例 2：

输入：s = "cbbd"
输出："bb
"""
class Solution:
    def longestPalindrome(self, s: str) -> str:
        """双指针: 中心扩展法，从中心向两边扩展，判断是否是回文串，如果是回文串，则更新最大长度和起始位置"""
        n = len(s)
        if n < 2:
            return s
        max_len = 1
        begin = 0
        for i in range(n):
            left = i - 1
            right = i + 1
            while right < n and s[right] == s[i]:
                right += 1
            while left >=0 and s[left] == s[i]:
                left -= 1
            while left >= 0 and right < n and s[left] == s[right]:
                left -= 1
                right += 1
            cur_len = right - left - 1
            if cur_len > max_len:
                max_len = cur_len
                begin = left + 1
        return s[begin:begin + max_len]

    def longestPalindrome_1(self, s: str) -> str:
        """动态规划, dp[i][j]表示s[i:j+1]是否是回文串 dp[i][j] = (s[i] == s[j]) and ((i - j < 3) or dp[i - 1][j + 1])"""
        n = len(s)
        dp = [[False] * n for _ in range(n)]
        begin = 0
        max_len = 1
        for i in range(n):
            dp[i][i] = True # 初始化
            for j in range(i - 1, -1, -1): # 从后往前遍历，避免重复计算
                dp[i][j] = (s[i] == s[j]) and ((i - j < 3) or dp[i - 1][j + 1])
                if dp[i][j] and i - j + 1 > max_len:
                    max_len = i - j + 1
                    begin = j

        return s[begin:begin + max_len]


if __name__ == '__main__':
    # print(Solution().longestPalindrome("babad"))
    print(Solution().longestPalindrome1("babad"))