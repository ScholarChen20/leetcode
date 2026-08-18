"""
给定整数数组 nums 和整数 k，请返回数组中第 k 个最大的元素。
    请注意，你需要找的是数组排序后的第 k 个最大的元素，而不是第 k 个不同的元素。
    你必须设计并实现时间复杂度为 O(n) 的算法解决此问题。
    示例 1:
    输入:[3,2,1,5,6,4] k=2
    输出： 5
    需要o(n)复杂度
"""
import heapq
import random
from typing import List
def findKthLargest(nums: List[int], k: int) -> int:
    # 利用最小堆维护前 K 大元素或快速选择分区。
    heap = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heappop(heap)
            heapq.heappush(heap, num)
    return heap[0]

def findKthLargest2(nums: List[int], k: int) -> int:
    # 快排分区 找打前k个最大元素
    privot = random.choice(nums)
    small, equal, large = [], [], []
    for num in nums:
        if num < privot:
            small.append(num)
        elif num == privot:
            equal.append(num)
        else:
            large.append(num)

    if k <= len(large): # 第 k 大元素在 large 中，递归划分
        return findKthLargest2(large, k)
    elif k > len(nums) - len(small): # # 第 k 大元素在 small 中，递归划分
        return findKthLargest2(small, k - len(large) - len(equal))
    return equal[0]

if __name__ == '__main__':
    # print(findKthLargest([3,2,1,5,6,4], 2))
    print(findKthLargest2([3,2,1,5,6,4], 2))