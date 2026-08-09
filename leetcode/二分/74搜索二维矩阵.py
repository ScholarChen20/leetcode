"""
74题 搜索二维矩阵
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
    print(searchMatrix([[1,3,5,7],[10,11,16,20],[23,30,34,50]], 100))