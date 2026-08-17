"""
以数组 intervals 表示若干个区间的集合，其中单个区间为 intervals[i] = [starti, endi] 。请你合并所有重叠的区间，并返回 一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间 。
示例 1：

输入：intervals = [[1,3],[2,6],[8,10],[15,18]]
输出：[[1,6],[8,10],[15,18]]
解释：区间 [1,3] 和 [2,6] 重叠, 将它们合并为 [1,6].
"""

class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        """
        先排序，然后合并,贪心选择下一个值左边界大于当前右边界进行合并
        """
        intervals.sort(key=lambda x: x[0])
        res = []
        for interval in intervals:
            if not res or res[-1][-1] < interval[0]:
                res.append(interval)
            else:
                res[-1][-1] = max(res[-1][-1], interval[-1])

        return res

if __name__ == '__main__':
    intervals = [[1,3],[2,6],[8,10],[15,18]]
    print(Solution().merge(intervals))