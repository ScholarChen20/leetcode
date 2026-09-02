"""
给你一个只包含 '(' 和 ')' 的字符串，找出最长有效（格式正确且连续）括号子串 的长度。
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
        """
        栈，栈中存储的是索引，栈底存储的是当前字符串的索引，栈顶存储的是当前字符串的索引
        遍历字符串，如果当前字符为'('，则将当前字符的索引入栈
        如果当前字符为')'，则将栈顶元素出栈，如果栈为空，则将当前字符的索引入栈
        否则，计算当前字符串的长度，更新ans
        返回ans
        """
        stack = []
        stack.append(-1)
        ans = 0
        for i in range(len(s)):
            if s[i] == '(':
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    stack.append(i)
                else:
                    ans = max(ans, i - stack[-1])
        return ans

    def longestValidParentheses_2(self, s: str) -> int:
        """
        一维dp，dp[i] 表示以 s[i] 结尾的最长有效括号子串的长度
        只有 s[i] == ')' 时才有可能形成新的有效子串：
        （1）若 s[i-1] == '('：dp[i] = dp[i-2] + 2
        （2）否则若 i-dp[i-1]-1 >= 0 且 s[i-dp[i-1]-1] == '('，说明 s[i] 与前面某个 '(' 配对：
            dp[i] = dp[i-1] + 2 + dp[i-dp[i-1]-2]
        """
        n = len(s)
        if n == 0:
            return 0
        dp = [0] * n
        for i in range(1, n):
            if s[i] == ')':
                if s[i - 1] == '(':
                    dp[i] = (dp[i - 2] if i >= 2 else 0) + 2
                else:
                    j = i - dp[i - 1] - 1
                    if j >= 0 and s[j] == '(':
                        dp[i] = dp[i - 1] + 2 + (dp[j - 1] if j >= 1 else 0)
        return max(dp)

if __name__ == '__main__':
    print(Solution().longestValidParentheses("()()"))
    # print(Solution().longestValidParentheses_2("()()"))