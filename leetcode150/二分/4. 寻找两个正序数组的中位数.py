"""
给定两个大小分别为 m 和 n 的正序（从小到大）数组 nums1 和 nums2。请你找出并返回这两个正序数组的 中位数 。
算法的时间复杂度应该为 O(log (m+n)) 。

示例 1：
输入：nums1 = [1,3], nums2 = [2]
输出：2.00000
解释：合并数组 = [1,2,3] ，中位数 2

示例 2：
输入：nums1 = [1,2], nums2 = [3,4]
输出：2.50000
解释：合并数组 = [1,2,3,4] ，中位数 (2 + 3) / 2 = 2.5
"""
from typing import List
class Solution:
    def findMedianSortedArrays2(self, nums1: List[int], nums2: List[int]) -> float:
        """思路： 在较短的数组上二分，可保证 j = half - i 的下标恒不越界 """
        # 确保在较短的数组上二分，可保证 j = half - i 的下标恒不越界
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        m, n = len(nums1), len(nums2)
        half = (m + n + 1) // 2  # 左半部分需要的元素总数
        left, right = 0, m

        while left <= right:
            # i: nums1 左半取 i 个元素; j: nums2 左半取 j 个元素, 满足 i + j == half
            i = (left + right) // 2
            j = half - i

            # 用 ±∞ 哨兵统一处理"一侧为空"的边界，省去 4 个 if 分支
            nums1_left_max = nums1[i - 1] if i > 0 else float("-inf")
            nums1_right_min = nums1[i] if i < m else float("inf")
            nums2_left_max = nums2[j - 1] if j > 0 else float("-inf")
            nums2_right_min = nums2[j] if j < n else float("inf")

            if nums1_left_max <= nums2_right_min and nums2_left_max <= nums1_right_min:
                # 划分合法：左半全部 <= 右半全部
                max_left = max(nums1_left_max, nums2_left_max)
                if (m + n) % 2 == 1:
                    return max_left
                return (max_left + min(nums1_right_min, nums2_right_min)) / 2
            elif nums1_left_max > nums2_right_min:
                # nums1 左半最大值过大，说明 i 取多了，向左收缩
                right = i - 1
            else:
                # nums2 左半最大值过大，说明 i 取少了，向右扩张
                left = i + 1

        return 0.0  # 理论不可达，仅为类型兜底