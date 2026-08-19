"""
给定一个 m x n 二维字符网格 board 和一个字符串单词 word 。
如果 word 存在于网格中，返回 true ；否则，返回 false 。
单词必须按照字母顺序，通过相邻的单元格内的字母构成，其中“相邻”单元格是那些水平相邻或垂直相邻的单元格。
同一个单元格内的字母不允许被重复使用。

示例 1：
输入：board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
输出：true
示例 2：
输入：board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "SEE"
输出：true
示例 3：
输入：board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCB"
输出：false
"""
from typing import List
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        """
        回溯
        """
        if not board or not word:
            return False
        visited = set()
        m, n = len(board), len(board[0])
        def facktrace(i, j, k):
            if board[i][j] == word[k]:
                if k == len(word) - 1:
                    return True
            visited.add((i, j))
            for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                if 0 <= x < m and 0 <= y < n and board[x][y] == word[k + 1]:
                    if facktrace(x, y, k + 1):
                        return True
            visited.remove((i, j))
            return False
        for i in range(m):
            for j in range(n):
                if facktrace(i, j, 0):
                    return True
        return False

if __name__ == '__main__':
    s = Solution()
    print(s.exist([["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], "ABCCED"))
