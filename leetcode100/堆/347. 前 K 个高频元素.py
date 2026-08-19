"""
给你一个整数数组 nums 和一个整数 k ，请你返回其中出现频率前 k 高的元素。你可以按 任意顺序 返回答案。
示例 1：

输入：nums = [1,1,1,2,2,3], k = 2
输出：[1,2]

示例 2：
输入：nums = [1], k = 1
输出：[1]
"""

import heapq
from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # 哈希表+最小堆
        count = {}
        for num in nums:
            count[num] = count[num] + 1 if num in count else 1
        heap = []
        for num, freq in count.items():
            if len(heap) < k:
                heapq.heappush(heap, (freq, num))
            elif freq > heap[0][0]:
                heapq.heappushpop(heap, (freq, num))
        return [num for freq, num in heap]

    def topKFrequent2(self, nums: List[int], k: int) -> List[int]:
        # 第一步：统计每个元素的出现次数
        count = Counter(nums)
        max_cnt = max(count.values())

        # 第二步：创建桶，将元素按照出现次数放入对应的桶中
        buckets = [[] for _ in range(max_cnt + 1)]
        for num, freq in count.items():
            buckets[freq].append(num)

        # 第三步：从后向前遍历桶，获取前 k 个高频元素
        res = []
        for bucket in reversed(buckets):
            res += bucket
            if len(res) >= k:
                break
        return res

    def topKFrequent3(self, nums: List[int], k: int) -> List[int]:
        return [key for key, value in Counter(nums).most_common(k)]

if __name__ == '__main__':
    # nums = list(map(int, input().split()))
    # print(Solution().topKFrequent(nums, k=2))
    print(Solution().topKFrequent2([1,1,1,2,2,3], 2))