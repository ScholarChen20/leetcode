"""
给定一个 n × n 的二维矩阵 matrix 表示一个图像。请你将图像顺时针旋转 90 度。
你必须在 原地 旋转图像，这意味着你需要直接修改输入的二维矩阵。请不要 使用另一个矩阵来旋转图像。

示例 1：
输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[[7,4,1],[8,5,2],[9,6,3]]
"""
from typing import List
class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        n = len(matrix)
        for i in range(n):
            for j in range(i, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        for i in range(n):
            matrix[i].reverse()

        return matrix

    def rotate2(self, matrix: List[List[int]]) -> None:
        # 创建一个新矩阵，用于存储旋转后的结果 时间复杂度O(n^2),空间复杂度O(n^2)
        n = len(matrix)
        new_matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(len(matrix[i])):
                new_matrix[j][n-1-i] = matrix[i][j]  # 顺时针旋转90度
        return new_matrix

if __name__ == '__main__':
    matrix = [[1,2,3],[4,5,6],[7,8,9]]
    # print(Solution().rotate(matrix))
    print(Solution().rotate2(matrix))


"""
矩阵转置:matrix[i][j] ↔ matrix[j][i]
矩阵水平镜像:matrix[i][j] ↔ matrix[i][n-1-j]
矩阵垂直镜像:matrix[i][j] ↔ matrix[m-1-i][j]
矩阵顺时针旋转90度， new_matrix[j][n-1-i] = matrix[i][j],就相当于垂直镜像+转置
矩阵顺时针旋转180度，new_matrix[n-1-i][n-1-j] = matrix[i][j],就相当于水平镜像+垂直镜像
矩阵逆时针旋转90度，new_matrix[n-1-j][i] = matrix[i][j],就相当于水平镜像+转置
matrix[:] = [list(row) for row in zip(*matrix[::-1])]
"""