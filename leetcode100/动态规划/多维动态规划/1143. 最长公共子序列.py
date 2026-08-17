"""
给定两个字符串 text1 和 text2，返回这两个字符串的最长 公共子序列 的长度。如果不存在 公共子序列 ，返回 0 。

一个字符串的 子序列 是指这样一个新的字符串：它是由原字符串在不改变字符的相对顺序的情况下删除某些字符（也可以不删除任何字符）后组成的新字符串。

例如，"ace" 是 "abcde" 的子序列，但 "aec" 不是 "abcde" 的子序列。
两个字符串的 公共子序列 是这两个字符串所共同拥有的子序列。



示例 1：

输入：text1 = "abcde", text2 = "ace"
输出：3
解释：最长公共子序列是 "ace" ，它的长度为 3 。
示例 2：

输入：text1 = "abc", text2 = "abc"
输出：3
解释：最长公共子序列是 "abc" ，它的长度为 3 。
示例 3：

输入：text1 = "abc", text2 = "def"
输出：0
解释：两个字符串没有公共子序列，返回 0 。
"""
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        """
        # 表示dp[i][j]表示text1[0:i]和text2[0:j]的最长公共子序列的长度
        外层循环遍历到m+1 内层循环n+1
        如果 text1的i-1位置字符等于text2的i-2位置字符串 dp[i][j] = dp[i-1][j-1] + 1
        否则的话 dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        最后记录此时的 ans = max(ans,dp[i][j]
        """
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)] # 表示dp[i][j]表示text1[0:i]和text2[0:j]的最长公共子序列的长度
        ans = 0
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                ans = max(ans, dp[i][j])
        return dp[-1][-1]

if __name__ == '__main__':
    print(Solution().longestCommonSubsequence("abcde", "ace"))

