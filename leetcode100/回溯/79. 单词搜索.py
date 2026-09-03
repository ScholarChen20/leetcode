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
        回溯，visited 记录已经访问过的节点，防止重复访问 k 记录当前匹配到的字符索引 i, j 表示当前节点的坐标
        如果 board[i][j] == word[k]，则继续匹配下一个字符，否则返回 False
        """
        if not board or not word:
            return False
        visited = set()
        m, n = len(board), len(board[0])
        def facktrace(i, j, k):
            if board[i][j] == word[k]: # 如果当前节点的字符等于 word 的第 k 个字符
                if k == len(word) - 1: # 如果 k 等于 word 的长度 - 1，说明已经匹配到 word 的最后一个字符，返回 True
                    return True
            visited.add((i, j))
            for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                if 0 <= x < m and 0 <= y < n and board[x][y] == word[k + 1]: # 如果下一个节点在 board 的范围内，且下一个节点的字符等于 word 的第 k + 1 个字符
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
