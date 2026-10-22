"""
给你一个 无重叠的 ，按照区间起始端点排序的区间列表 intervals，其中 intervals[i] = [starti, endi] 表示第 i 个区间的开始和结束，并且 intervals 按照 starti 升序排列。同样给定一个区间 newInterval = [start, end] 表示另一个区间的开始和结束。
如果两个区间 至少 共享一个点，则认为它们是重叠的。
在 intervals 中插入区间 newInterval，使得 intervals 依然按照 starti 升序排列，且区间之间不重叠（如果有必要的话，可以合并区间）。
返回插入之后的 intervals。注意 你不需要原地修改 intervals。你可以创建一个新数组然后返回它。

示例 1：

输入：intervals = [[1,3],[6,9]], newInterval = [2,5]
输出：[[1,5],[6,9]]
示例 2：

输入：intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
输出：[[1,2],[3,10],[12,16]]
解释：这是因为新的区间 [4,8] 与 [3,5],[6,7],[8,10] 重叠。
"""
from typing import List
class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        """时间复杂度O(n)，空间复杂度O(n)"""
        res = []
        i = 0
        n = len(intervals)
        while i < n and intervals[i][1] < newInterval[0]: # 找到第一个与newInterval不重叠的区间
            res.append(intervals[i])
            i += 1

        while i < n and intervals[i][0] <= newInterval[1]: # 找到第一个与newInterval重叠的区间
            newInterval[0] = min(newInterval[0], intervals[i][0]) # 更新newInterval的左端点
            newInterval[1] = max(newInterval[1], intervals[i][1]) # 更新newInterval的右端点
            i += 1

        res.append(newInterval) # 将newInterval插入到res中

        while i < n: # 将剩余的区间插入到res中
            res.append(intervals[i])
            i += 1

        return res

if __name__ == '__main__':
    s = Solution()
    intervals = [[1,3],[6,9]]
    newInterval = [2,5]
    print(s.insert(intervals, newInterval))
