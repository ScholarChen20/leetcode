"""
给你一个整数数组 nums ，找到其中最长严格递增子序列的长度。
子序列 是由数组派生而来的序列，删除（或不删除）数组中的元素而不改变其余元素的顺序。例如，[3,6,2,7] 是数组 [0,3,1,6,2,2,7] 的子序列。
示例 1：
输入：nums = [10,9,2,5,3,7,101,18]
输出：4
解释：最长递增子序列是 [2,3,7,101]，因此长度为 4 。
示例 2：
输入：nums = [0,1,0,3,2,3]
输出：4
示例 3：
输入：nums = [7,7,7,7,7,7,7]
输出：1
"""
from typing import List
class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        """二分查找 O(nlogn), 定义ans"""
        ans = []
        for i in nums:
            if not ans or i > ans[-1]:
                ans.append(i)
            else:
                left = 0
                right = len(ans) - 1
                while left < right:
                    mid = (left + right) // 2
                    if ans[mid] < i: # 找到第一个大于等于i的数
                        left = mid + 1
                    else:
                        right = mid
                ans[left] = i # 更新ans
        return len(ans)

    """动态规划 O(n^2) dp[i]表示以nums[i]结尾的最长子序列长度 dp[i] = max(dp[i], dp[j] + 1) """
    def lengthOfLIS_1(self, nums: List[int]) -> int:
        n = len(nums)

        dp = [1] * n
        for i in range(n):
            for j in range(i):
                if  nums[i] > nums[j]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)

    """动态规划＋2分查询 定义 tails, res = 0 tails[i]表示长度为i的最长子序列的最小末尾元素"""
    def lengthOfLIS_2(self, nums: List[int]) -> int:
        tails = [0] * len(nums)
        res = 0
        for num in nums:
            left = 0
            right = res
            while left < right:
                mid = (left + right) // 2
                if tails[mid] < num:
                    left = mid + 1
                else:
                    right = mid
            tails[left] = num
            if left == res: # 如果left==res,说明num大于所有tails中的元素，res+1
                res += 1
        return res


if __name__ == '__main__':
    # print(Solution().lengthOfLIS([0,1,0,3,2,3]))
    print(Solution().lengthOfLIS([10,9,2,5,3,7,101,18]))