"""
给定两个以升序排列的整形数组 nums1 和 nums2, 以及一个整数 k。
定义一对值 (u,v)，其中第一个元素来自 nums1，第二个元素来自 nums2。
找到和最小的 k 对数字 (u1,v1), (u2,v2) ... (uk,vk)。

示例 1:
输入: nums1 = [1,7,11], nums2 = [2,4,6], k = 3
输出: [1,2],[1,4],[1,6]
解释: 返回序列中的前 3 对数：
     [1,2],[1,4],[1,6],[7,2],[7,4],[11,2],[7,6],[11,4],[11,6]
示例 2：
输入: nums1 = [1,2], nums2 = [3], k = 3
输出: [1,3],[2,3]
解释: 虽然有三个数对，但只有两个不同的数对，所以返回这两个数对
"""
import heapq
from typing import List


class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        """最小堆"""
        heap = []
        for i in range(len(nums1)):
            for j in range(len(nums2)):
                if len(heap) < k:
                    heapq.heappush(heap, (nums1[i] + nums2[j], nums1[i], nums2[j]))
                elif nums1[i] + nums2[j] < heap[0][0]:
                    heapq.heappop(heap)
                    heapq.heappush(heap, (nums1[i] + nums2[j], nums1[i], nums2[j]))
                else:
                    break
        return [[x, y] for _, x, y in heap]