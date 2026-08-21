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
        """
        if not height:
            return 0
        n = len(height)
        ans = 0
        left, right = 0, n-1
        lmax, rmax = 0, 0
        # 分别记录遍历到的左边最大值和右边最大值
        while  left < right:
            lmax = max(lmax, height[left])
            rmax = max(rmax, height[right])

            # 从左右最大值中较小的值开始计算接雨水量
            if lmax < rmax:
                ans += lmax - height[left]
                left += 1
            else:
                ans += rmax - height[right]
                right -= 1

        return ans

    def trap1(self, height: List[int]) -> int:
        """
        动态规划解法：先计算每个位置的左右最大值，然后计算每个位置的接雨水量。时间复杂度O(n)，空间复杂度O(n)
        """
        n = len(height)
        left_max = [0] * n
        right_max = [0] * n
        left_max[0] = height[0]
        right_max[n-1] = height[n-1]
        for i in range(1, n):
            left_max[i] = max(left_max[i-1], height[i])
        for i in range(n-2, -1, -1):
            right_max[i] = max(right_max[i+1], height[i])

        ans = 0
        for i in range(n):
            ans += min(left_max[i], right_max[i]) - height[i] # 当前高度和左右最大值的较小值的差值

        return ans

    def trap2(self, height: List[int]) -> int:
        """单调栈解法： 维护一个单调递减栈，栈中存储的是下标，栈中元素对应的 height 递减，当遍历到的元素大于栈顶元素时，说明当前元素可以接雨水，接雨水量为当前元素和栈顶元素的差值乘以栈顶元素的宽度
        """
        n = len(height)
        stack = []
        ans = 0
        for i in range(n):
            while stack and height[i] > height[stack[-1]]:
                top = stack.pop() # 栈顶元素
                if not stack:
                    break
                left = stack[-1] # 栈顶元素的左边元素
                curr_width = i - left - 1 # 当前元素和栈顶元素的宽度
                curr_height = min(height[i], height[left]) - height[top] # 当前元素和栈顶元素的高度差
                ans += curr_width * curr_height
            stack.append(i)
        return ans

if __name__ == '__main__':
    s = Solution()
    height = [0,1,0,2,1,0,1,3,2,1,2,1]
    # print(s.trap(height))
    # print(s.trap1(height))
    print(s.trap2(height))