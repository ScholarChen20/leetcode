"""
n皇后问题
按照国际象棋的规则，皇后可以攻击与之处在同一行或同一列或同一斜线上的棋子。

n 皇后问题 研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。

给你一个整数 n ，返回所有不同的 n 皇后问题 的解决方案。

每一种解法包含一个不同的 n 皇后问题 的棋子放置方案，该方案中 'Q' 和 '.' 分别代表了皇后和空位。
输入：n = 4
输出：[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
"""
from typing import List
class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        """
        回溯法 + 剪枝
        """
        res = []
        path = [["."] * n for _ in range(n)]
        self.backtrack(path, 0, n, res)
        return res

    def backtrack(self, path, row, n, res):
        if row == n:
            res.append([''.join(row) for row in path])
            return
        for col in range(n):
            if self.isValid(path, row, col, n):
                path[row][col] = "Q"
                self.backtrack(path, row + 1, n, res)
                path[row][col] = "."
                # print( path)

    def isValid(self, path, row, col, n):
        for i in range(row): # 判断列是否有皇后
            if path[i][col] == "Q":
                return False
        i, j = row - 1, col - 1  # 左上角, i >= 0 保证不会越界 j >= 0 保证不会越界
        while i >= 0 and j >= 0:
            if path[i][j] == "Q":
                return False
            i -= 1
            j -= 1
        i, j = row - 1, col + 1 # 右上角, i >= 0 保证不会越界 j < n 保证不会越界
        while i >= 0 and j < n:
            if path[i][j] == "Q":
                return False
            i -= 1
            j += 1

        return True

if __name__ == '__main__':
    print(Solution().solveNQueens(4))