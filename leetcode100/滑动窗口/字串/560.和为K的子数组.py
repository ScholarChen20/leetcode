"""
给你一个整数数组 nums 和一个整数 k ，请你统计并返回 该数组中和为 k 的子数组的个数 。
子数组是数组中元素的连续非空序列。
示例 1：

输入：nums = [1,1,1], k = 2
输出：2
示例 2：

输入：nums = [1,2,3], k = 3
输出：2
"""


from collections import defaultdict
from typing import List
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        n=len(nums)
        if n==1 and nums[0]!=k:
            return 0
        ans=num=0
        cnt = defaultdict(int)
        cnt[0]=1
        for x in nums:
            num+=x
            ans+=cnt[num-k]
            cnt[num]+=1
        return ans