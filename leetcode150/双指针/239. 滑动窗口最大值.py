"""
给你一个整数数组 nums，有一个大小为 k 的滑动窗口从数组的最左侧移动到最右侧。你只可以看到窗口中的 k 个数字。滑动窗口每次只向右移动一位。
返回滑动窗口中的最大值。

示例
输入：nums = [1,3,-1,-3,5,3,6,7], k = 3
输出：[3,3,5,5,6,7]
输入：nums = [1], k = 1
输出：[1]
"""
import collections
from typing import List
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        n = len(nums)
        q = collections.deque()
        for i in range(k):
            while q and nums[i] >= nums[q[-1]]:
                q.pop()
            q.append(i)

        ans = [nums[q[0]]]
        for i in range(k, n):
            while q and nums[i] >= nums[q[-1]]:
                q.pop()
            q.append(i)
            while q[0] <= i - k: # 保证队列中存储的是窗口中的元素
                q.popleft()
            ans.append(nums[q[0]])

        return ans


if __name__ == '__main__':
    s = Solution()
    print(s.maxSlidingWindow(nums=[1,3,-1,-3,5,3,6,7], k=3))

