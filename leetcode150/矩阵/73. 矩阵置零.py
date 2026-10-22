"""
给定一个 m x n 的矩阵，如果一个元素为 0 ，则将其所在行和列的所有元素都设为 0 。请使用 原地 算法。
示例 1：

输入：matrix = [[1,1,1],[1,0,1],[1,1,1]]
输出：[[1,0,1],[0,0,0],[1,0,1]]

输入：matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
输出：[[0,0,0,0],[0,4,5,0],[0,3,1,0]]
"""
from typing import List


class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        """
        使用标记数组， 时间复杂度O(mn),空间复杂度O(m+n)
        """
        m, n = len(matrix), len(matrix[0])
        row, col = [False] * m, [False] * n
        for i in range(m):
            for j in range(n):
                if matrix[i][j] == 0:
                    row[i] = True
                    col[j] = True
        for i in range(m):
            for j in range(n):
                if row[i] or col[j]:
                    matrix[i][j] = 0

        return matrix


class Solution1:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        # 使用两个标记变量，分别记录第一行和第一列是否需要置零
        m, n = len(matrix), len(matrix[0])
        flag_col0 = any(matrix[i][0] == 0 for i in range(m))
        flag_row0 = any(matrix[0][j] == 0 for j in range(n))

        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][j] == 0:
                    matrix[i][0] = matrix[0][j] = 0

        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0

        if flag_col0:
            for i in range(m):
                matrix[i][0] = 0

        if flag_row0:
            for j in range(n):
                matrix[0][j] = 0

        return matrix


class Solution3:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        # 使用一个标记变量，记录第一列是否需要置零
        m, n = len(matrix), len(matrix[0])
        flag_col0 = False

        for i in range(m):
            if matrix[i][0] == 0: # 记录第一列是否需要置零
                flag_col0 = True
            for j in range(1, n): # 从第二列开始，记录各行各列是否需要置零
                if matrix[i][j] == 0:
                    matrix[i][0] = matrix[0][j] = 0

        for i in range(m - 1, -1, -1):  # 从后向前遍历，避免第二步中对第一列元素的修改，影响后续对行的判断
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
            if flag_col0: # 最后处理第一列
                matrix[i][0] = 0


if __name__ == '__main__':
    matrix = [[1,1,1],[1,0,1],[1,1,1]]
    matrix1 = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
    print(Solution1().setZeroes(matrix1))