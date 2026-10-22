"""
以数组 intervals 表示若干个区间的集合，其中单个区间为 intervals[i] = [starti, endi] 。请你合并所有重叠的区间，并返回 一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间 。

示例 1：

输入：intervals = [[1,3],[2,6],[8,10],[15,18]]
输出：[[1,6],[8,10],[15,18]]
解释：区间 [1,3] 和 [2,6] 重叠, 将它们合并为 [1,6].
示例 2：

输入：intervals = [[1,4],[4,5]]
输出：[[1,5]]
解释：区间 [1,4] 和 [4,5] 可被视为重叠区间。
"""
from typing import List
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        # 贪心 时间复杂度O(nlogn)，空间复杂度O(n)
        if not intervals:
            return []
        intervals.sort(key = lambda x: x[0]) # 按照区间的左端点排序
        merged = []
        for interval in intervals:
            if not merged or merged[-1][1] < interval[0]:
                merged.append(interval)
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])
        return merged

if __name__ == '__main__':
    s = Solution()
    test_intervals = [[1,3],[2,6],[8,10],[15,18]]
    print(s.merge(test_intervals))