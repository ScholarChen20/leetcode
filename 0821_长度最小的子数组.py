"""
长度最小的子数组
给定一个含有 n个正整数的数组和一个正整数 target 。找出该数组中满足其和 ≥ target 的长度最小的 连续子数组，并返回其长度。如果不存在符合条件的子数组，返回 0  示例 1：
输入：target = 7, nums = [2,3,1,2,4,3]
输出：2
解释：子数组 [4,3] 是该条件下的长度最小的子数组。
"""
from cmath import inf
from typing import List
class Solution:
    def minDistance(self, target: int, nums: List[int]) -> int:
        """滑动窗口"""
        left ,right = 0,0 # 窗口的左右指针
        ans = inf # 最小长度
        sum = 0 # 窗口内元素和
        while right < len(nums):
            sum += nums[right]
            while sum >= target:
                if sum == target:
                    ans = min(ans, right - left + 1)
                sum -= nums[left]
                left +=1
            right += 1
        return ans if ans != inf else 0



if __name__ == '__main__':
    # target = int(input())
    # nums = list(map(int, input().split()))
    print(Solution().minDistance(16, [2,3,1,2,4,3]))

