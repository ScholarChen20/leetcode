"""
给你一个 只包含正整数 的 非空 数组 nums 。请你判断是否可以将这个数组分割成两个子集，使得两个子集的元素和相等。
示例 1：

输入：nums = [1,5,11,5]
输出：true
解释：数组可以分割成 [1, 5, 5] 和 [11] 。
示例 2：

输入：nums = [1,2,3,5]
输出：false
解释：数组不能分割成两个元素和相等的子集。

"""
from typing import List
class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        # 先判断n的长度，如果n的长度小于2，则返回false
        n = len(nums)
        if n < 2:
            return False
        total = sum(nums)
        if total & 1:
            return False
        maxNum = max(nums)
        if maxNum > total // 2:
            return False

        j = maxNum // 2
        dp = [[False] * (total // 2 + 1) for _ in range(n)]
        # 定义dp[i][j]表示【0，i】位置的元素，是否可以找到一个子集，使得子集的和为j
        for i in range(n):
            dp[i][0] = True
        dp[0][nums[0]] = True

        for i in range(1, n):
            for j in range(total // 2 + 1):
                if j >= nums[i]:
                    dp[i][j] = dp[i - 1][j] or dp[i - 1][j - nums[i]]
                else:
                    dp[i][j] = dp[i - 1][j]

        return dp[-1][-1]

class Solution1:
    def canPartition(self, nums: List[int]) -> bool:
        """
        一维dp
        """
        n = len(nums)
        if n < 2:
            return False

        total = sum(nums)
        if total & 1:
            return False

        target = total // 2
        dp = [True] + [False] * target
        for i in range(1, n):
            for j in range(target, nums[i] - 1, -1):
                dp[j] = dp[j] | dp[j - nums[i]]
        return dp[-1]

if __name__ == '__main__':
    print(Solution1().canPartition([1,2,2,5]))