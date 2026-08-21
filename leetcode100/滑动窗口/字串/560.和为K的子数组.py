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
        """ 暴力解法，时间复杂度O(n^2)，空间复杂度O(1)"""
        n=len(nums)
        if n==1 and nums[0]!=k:
            return 0
        res=0
        for i in range(n):
            sum=0
            for j in range(i,n):
                sum+=nums[j]
                if sum==k:
                    res+=1
        return res

    def subarraySum2(self, nums: List[int], k: int) -> int:
        """前缀和，时间复杂度O(n^2)，空间复杂度O(n) """
        n = len(nums)
        pre_sum = [0] * (n + 1)
        for i in range(1, n + 1):
            pre_sum[i] = pre_sum[i - 1] + nums[i - 1]

        res=0
        for i in range(n):
            for j in range(i+1,n+1):
                if pre_sum[j]-pre_sum[i]==k:
                    res+=1
        return res

    def subarraySum3(self, nums: List[int], k: int) -> int:
        """前缀和+哈希表，时间复杂度O(n)，空间复杂度O(n) """
        n=len(nums)
        pre_sum=0
        res=0
        hash_map=defaultdict(int)
        hash_map[0]=1
        for i in range(n):
            pre_sum += nums[i]
            if pre_sum - k in hash_map:
                res+=hash_map[pre_sum - k]

            hash_map[pre_sum] += 1
        return res

if __name__ == '__main__':
    s=Solution()
    # print(s.subarraySum([1,1,1], 2))
    # print(s.subarraySum([1,2,3,3], 3))
    print(s.subarraySum3([1,2,3,3,2,1], 3))