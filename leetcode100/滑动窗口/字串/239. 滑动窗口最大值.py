"""
给你一个整数数组 nums，有一个大小为 k 的滑动窗口从数组的最左侧移动到数组的最右侧。你只可以看到在滑动窗口内的 k 个数字。滑动窗口每次只向右移动一位。
返回 滑动窗口中的最大值 。

示例 1：

输入：nums = [1,3,-1,-3,5,3,6,7], k = 3
输出：[3,3,5,5,6,7]
"""
import collections
from typing import List
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        """
        维护一个队列，队列中存储的是数组的下标，队列中的元素是单调递减的，队列中的第一个元素就是滑动窗口的最大值
        时间复杂度：O(n)
        空间复杂度：O(k)
        """
        queue = collections.deque()
        res = []
        n = len(nums)
        for i,j in zip(range(1-k,n-k+1), range(n)):
            # 删除 deque 中对应的 nums[i-1]
            if i>0 and queue[0] == nums[i-1]:
                queue.popleft()
            # 保持 deque 递减
            while queue and queue[-1] < nums[j]:
                queue.pop()
            queue.append(nums[j])
            if i >= 0:
                res.append(queue[0])
        return res

if __name__ == '__main__':
    s = Solution()
    nums = [1,3,-1,-3,5,3,6,7]
    k = 3
    print(s.maxSlidingWindow(nums, k))
