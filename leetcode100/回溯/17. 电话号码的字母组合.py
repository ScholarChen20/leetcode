"""
给定一个仅包含数字 2-9 的字符串，返回所有它能表示的字母组合。答案可以按 任意顺序 返回。
给出数字到字母的映射如下（与电话按键相同）。注意 1 不对应任何字母。

示例 1：

输入：digits = "23"
输出：["ad","ae","af","bd","be","bf","cd","ce","cf"]
示例 2：

输入：digits = "2"
输出：["a","b","c"]
"""
from typing import List
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        """
        思路：回溯 + 剪枝
        1. 从 digits
        2. 递归调用 facktrace 函数，index + 1
        """
        if not digits:
            return []
        phone = {
            '2': ['a', 'b', 'c'],
            '3': ['d', 'e', 'f'],
            '4': ['g', 'h', 'i'],
            '5': ['j', 'k', 'l'],
            '6': ['m', 'n', 'o'],
            '7': ['p', 'q', 'r', 's'],
            '8': ['t', 'u', 'v'],
            '9': ['w', 'x', 'y', 'z']
        }
        res = []
        def facktrace(path, index):
            if index == len(digits): # 终止条件
                res.append("".join(path)) # 满足条件
                return
            for i in phone[digits[index]]: # 遍历当前数字对应的字母
                path.append(i) # 选择
                facktrace(path, index + 1) # 递归
                path.pop()  # 撤销选择
        facktrace([], 0)
        return res

if __name__ == '__main__':
    s = Solution()
    # print(s.letterCombinations("23"))
    print(s.letterCombinations("2"))