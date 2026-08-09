"""
215. 数组中的第K个最大元素
"""
import heapq
from typing import List


def findKthLargest(nums: List[int], k: int) -> int:
    """
    给定整数数组 nums 和整数 k，请返回数组中第 k 个最大的元素。
    请注意，你需要找的是数组排序后的第 k 个最大的元素，而不是第 k 个不同的元素。
    你必须设计并实现时间复杂度为 O(n) 的算法解决此问题。
    示例 1:
    输入:[3,2,1,5,6,4] k=2
    输出： 5
    需要o(n)复杂度
    """
    # 利用最小堆维护前 K 大元素或快速选择分区。
    heap = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heappop(heap)
            heapq.heappush(heap, num)
    return heap[0]


if __name__ == '__main__':
    print(findKthLargest([3,2,1,5,6,4], 2))