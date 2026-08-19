"""
数字 n 代表生成括号的对数，请你设计一个函数，用于能够生成所有可能的并且 有效的 括号组合。

示例 1：

输入：n = 3
输出：["((()))","(()())","(())()","()(())","()()()"]
示例 2：

输入：n = 1
输出：["()"]
"""
from typing import List
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        """
        思路：回溯 + 剪枝
        1. left 表示剩余的左括号数，right 表示剩余的右括号数
        2. 如果 left > 0，则可以添加左括号，left - 1
        3. 如果 right > 0 且 left < right，则可以添加右括号，right - 1
        """
        res = []
        def facktrace(path, left, right):
            if left ==0 and right == 0: # 找到一个解
                res.append(path)
                return
            if left > 0:
                facktrace(path + "(", left - 1, right) # 左括号
            if right > 0 and left < right:
                facktrace(path + ")", left, right - 1) # 右括号
        facktrace("", n, n) # n 个左括号，n 个右括号
        return res

if __name__ == '__main__':
    s = Solution()
    print(s.generateParenthesis(3))
