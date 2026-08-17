"""
给你一个只包含 '(' 和 ')' 的字符串，找出最长有效（格式正确且连续）括号 子串 的长度。
左右括号匹配，即每个左括号都有对应的右括号将其闭合的字符串是格式正确的，比如 "(()())"。
示例 1：

输入：s = "(()"
输出：2
解释：最长有效括号子串是 "()"
示例 2：

输入：s = ")()())"
输出：4
解释：最长有效括号子串是 "()()"
示例 3：

输入：s = ""
输出：0
"""
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        stack = []
        ans = 0
        for i,str in enumerate(s):
            if str == '(':
                stack.append(i)
            else:
                if not stack:
                    stack.append(i)
                else:
                    stack.pop()
                    if not stack:
                        stack.append( i)
                    else:
                        ans = max(ans, i - stack[-1])
        return ans

class Solution1:
    """
    一维dp，假设dp[i]为前i个字符中最长的有效括号个数
    初始化字符串长度的dp数组
    遍历字字符串 若出现当前字符为'(' 则设当前dp[i]为0
    否则 判断前一个字符是否为’)' ：
    （1）是的话直接dp[i] = dp[i - 2] + 2 个数加2
    （2）否则判断i - dp[i - 1] > 0 and s[i - dp[i - 1] - 1] == '('是否成立，成立的话dp[i] = dp[i - 1] + 2 + dp[i - dp[i - 1] - 2]
    """
    def longestValidParentheses(self, s: str) -> int:
        dp = [0] * len(s)
        for i in range(0, len(s)):
            if s[i] == ')':
                if s[i - 1] == '(':
                    dp[i] = dp[i - 2] + 2
                elif i - dp[i - 1] > 0 and s[i - dp[i - 1] - 1] == '(':
                    dp[i] = dp[i - 1] + 2 + dp[i - dp[i - 1] - 2]
            else:
                dp[i] = 0
        return max(dp)

if __name__ == '__main__':
    # print(Solution1().longestValidParentheses(")()())"))
    # print(Solution1().longestValidParentheses("(())"))
    print(Solution1().longestValidParentheses("(()"))