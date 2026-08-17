"""
编写一个高效的算法来搜索 m x n 矩阵 matrix 中的一个目标值 target 。该矩阵具有以下特性：
每行的元素从左到右升序排列。
每列的元素从上到下升序排列。

示例 1：
输入：matrix = [[1,4,7,11,15],[2,5,8,12,19],[3,6,9,16,22],[10,13,14,17,24],[18,21,23,26,30]], target = 5
输出：true
"""
from typing import List

from sympy import true


class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        "二分搜索加一维数组铺平"
        m, n = len(matrix), len(matrix[0])
        left ,right = 0, m*n -1

        while left < right:
            mid = (left + right) // 2
            row = mid % m
            col = mid % n
            if matrix[row][col] == target:
                return true
            elif matrix[row][col] < target:
                left = mid + 1
            else:
                right = mid - 1

        return False


class Solution1:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        i,j =  0, len(matrix[0]) - 1,
        while j >= 0 and i < len(matrix[0]):
            if matrix[i][j] < target: i+= 1
            elif matrix[i][j] > target: j-=1
            else: return True

        return False



if __name__ == '__main__':
    matrix = [[1,4,7,11,15],[2,5,8,12,19],[3,6,9,16,22],[10,13,14,17,24],[18,21,23,26,30]]
    target = 20
    print(Solution1().searchMatrix(matrix, target))
