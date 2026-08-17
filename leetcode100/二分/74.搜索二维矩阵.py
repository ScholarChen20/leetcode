"""
给你一个满足下述两条属性的 m x n 整数矩阵：

每行中的整数从左到右按非严格递增顺序排列。
每行的第一个整数大于前一行的最后一个整数。
给你一个整数 target ，如果 target 在矩阵中，返回 true ；否则，返回 false 。
输入：matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
输出：true
"""
from typing import List
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int):
        m, n = len(matrix), len(matrix[0])
        left, right = 0, m * n - 1
        while left < right:
            mid = (left + right) // 2
            x, y = mid // n, mid % n
            if matrix[x][y] < target:
                left = mid + 1
            else:
                right = mid

        return matrix[left // n][left % n] == target