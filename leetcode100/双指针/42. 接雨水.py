"""
给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。

输入：height = [0,1,0,2,1,0,1,3,2,1,2,1]
输出：6
解释：上面是由数组 [0,1,0,2,1,0,1,3,2,1,2,1] 表示的高度图，在这种情况下，可以接 6 个单位的雨水（蓝色部分表示雨水）。
"""
from typing import List


class Solution:
    def trap(self, height: List[int]) -> int:
        """
        注意到下标 i 处能接的雨水量由 leftMax[i] 和 rightMax[i] 中的最小值决定。由于数组 leftMax 是从左往右计算，数组 rightMax 是从右往左计算，因此可以使用双指针和两个变量代替两个数组。
        :param height:
        :return:
        """
        if not height:
            return 0
        n=len(height)
        ans=0
        leftmax=0
        rightmax=n-1
        lmax,rmax=0,0

        # 分别记录遍历到的左边最大值和右边最大值
        while  leftmax < rightmax:
            lmax=max(lmax,height[leftmax])
            rmax=max(rmax,height[rightmax])

            # 指针走向
            if lmax<rmax:
                ans+=lmax-height[leftmax]
                leftmax+=1
            else:
                ans+=rmax-height[rightmax]
                rightmax-=1

        return ans


class Solution1:
    def trap(self, height: List[int]) -> int:
        """
        动态规划解法 or 单调栈解法 TODO
        """

if __name__ == '__main__':
    s = Solution()
    height = [0,1,0,2,1,0,1,3,2,1,2,1]
    print(s.trap(height))