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
    def findKth(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        求两个有序数组的第 k 小（k 从 1 开始）。
        核心思想：每轮在两个数组各取 k//2 个候选元素做比较，
        较小一侧的候选整体不可能包含第 k 小，直接排除，使 k 减半。
        """
        m, n = len(nums1), len(nums2)
        i = j = 0  # 两个数组当前未排除部分的起始下标
        while True:
            # 某个数组已排空，第 k 小必然在另一个数组的剩余部分
            if i == m:
                return nums2[j + k - 1]
            if j == n:
                return nums1[i + k - 1]
            # k == 1 时取两个数组当前头部的最小值
            if k == 1:
                return min(nums1[i], nums2[j])

            half = k // 2
            ni = min(i + half, m)  # nums1 的候选上界（越界则取到末尾）
            nj = min(j + half, n)  # nums2 的候选上界（越界则取到末尾）
            if nums1[ni - 1] <= nums2[nj - 1]:
                # nums1 的前 (ni - i) 个元素都 <= nums2[nj-1]，至多排第 k 名之前，可排除
                k -= ni - i
                i = ni
            else:
                k -= nj - j
                j = nj

    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        total = len(nums1) + len(nums2)
        if total % 2 == 1:
            return self.findKth(nums1, nums2, total // 2 + 1)
        # 偶数个元素：中位数 = 中间两个数的平均
        return (self.findKth(nums1, nums2, total // 2)
                + self.findKth(nums1, nums2, total // 2 + 1)) / 2


if __name__ == '__main__':
    s = Solution()
    # print(s.findMedianSortedArrays([1, 3], [2]))      # 2.0
     # print(s.findMedianSortedArrays([1, 2], [3, 4]))   # 2.5
    print(s.findKth([1, 2], [3, 4], 2))
