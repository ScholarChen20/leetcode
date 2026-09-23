"""
给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s ，判断字符串是否有效。
有效字符串需满足：
左括号必须用相同类型的右括号闭合。
左括号必须以正确的顺序闭合。
每个右括号都有一个对应的相同类型的左括号。

示例 1：
输入：s = "()"
输出：true

示例 2：
输入：s = "()[]{}"
输出：true
"""
class Solution:
    def isValid(self, s: str) -> bool:
        """解法一：单调栈"""
        mapping = {')': '(', ']': '[', '}': '{'}
        stack = []
        for c in s:
            if c in '([{':
                stack.append(c)
            else:
                if not stack or stack[-1] != mapping[c]:
                    return False
                stack.pop()
        return not stack

    def isValid2(self, s: str) -> bool:
        """解法二： 使用replace方法"""
        while '()' in s or '[]' in s or '{}' in s:
            s = s.replace('()', '').replace('[]', '').replace('{}', '')
        return not s


if __name__ == '__main__':
    # print(Solution().isValid("()"))
    # print(Solution().isValid("()[]{}"))
    print(Solution().isValid("([)]"))