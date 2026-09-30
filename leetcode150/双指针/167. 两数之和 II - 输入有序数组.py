"""
给定一个已按照 非递减顺序排列 的整数数组numbers，请你从数组中找出两个数满足相加之和等于目标数target。
函数应该以长度为 2 的整数数组的形式返回这两个数的下标值。numbers 的下标 从 1 开始计数 ，所以答案数组应当满足 1 <= answer[0] < answer[1] <= numbers.length。
你可以假设每个输入只对应唯一的答案，而且你不可以重复使用相同的元素。

输入：numbers = [2,7,11,15], target = 9
输出：[1,2]
解释：2 与 7 之和等于目标数 9 。因此 index1 = 1, index2 = 2 。
"""
from typing import List


class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        """解法一：双指针；时间复杂度O(n)"""
        left, right = 0, len(numbers) - 1
        while left < right:
            if numbers[left] + numbers[right] == target:
                return [left + 1, right + 1]
            elif numbers[left] + numbers[right] < target:
                left += 1
            else:
                right -= 1
        return []

    def twoSum_2(self, numbers: List[int], target: int) -> List[int]:
        """解法二：二分查找；时间复杂度O(nlogn)"""
        for i in range(len(numbers)):
            left, right = i + 1, len(numbers) - 1
            while left <= right:
                mid = (left + right) // 2
                if numbers[mid] == target - numbers[i]:
                    return [i + 1, mid + 1]
                elif numbers[mid] < target - numbers[i]:
                    left = mid + 1
                else:
                    right = mid - 1
        return []

if __name__ == '__main__':
    s = Solution()
    print(s.twoSum([2,7,11,15], 9))
    print(s.twoSum_2([2,7,11,15], 9))