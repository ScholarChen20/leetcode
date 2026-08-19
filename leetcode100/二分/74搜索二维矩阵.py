"""
给你一个满足下述两条属性的 m x n 整数矩阵：

每行中的整数从左到右按非严格递增顺序排列。
每行的第一个整数大于前一行的最后一个整数。
给你一个整数 target ，如果 target 在矩阵中，返回 true ；否则，返回 false 。

输入：matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
输出：true
"""
from typing import List


def searchMatrix(matrix: List[List[int]], target: int) -> bool:
    """
    """
    m = len(matrix)
    n = len(matrix[0])
    left = 0
    right = m * n - 1
    while left < right:
        mid = int((left + right) / 2) +1
        row = int(mid / n)
        column = mid % n
        if matrix[row][column] == target:
            return True
        elif matrix[row][column] > target:
            right = mid - 1
        else:
            left = mid + 1
    return False

if __name__ == '__main__':
    # 自定义输入矩阵元素
    # 自定义输入目标值
    target = int(input())
    m ,n = map(int, input().split())
    matrix = []
    for i in range(m):
        matrix.append(list(map(int, input().split())))
    print(searchMatrix([[1,3,5,7],[10,11,16,20],[23,30,34,50]], 100))