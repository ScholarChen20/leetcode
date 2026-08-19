"""
给定 n 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 1 。
求在该柱状图中，能够勾勒出来的矩形的最大面积。
示例 1:

输入：heights = [2,1,5,6,2,3]
输出：10
解释：最大的矩形为图中红色区域，面积为 10

输入： heights = [2,4]
输出： 4
"""
from typing import List
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        """单调栈存索引，栈中存的是索引，栈中索引对应的值是递增的"""
        stack = []
        ans = 0
        heights.append(0)
        for i,h in enumerate(heights):
            while stack and heights[stack[-1]] > h:
                height = heights[stack.pop()]
                width = i - stack[-1] - 1 if stack else i
                ans = max(ans, height * width)
            stack.append(i)

        return ans

if __name__ == '__main__':
    print(Solution().largestRectangleArea([2,1,5,6,2,3]))
