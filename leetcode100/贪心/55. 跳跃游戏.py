"""
给你一个非负整数数组 nums ，你最初位于数组的 第一个下标 。数组中的每个元素代表你在该位置可以跳跃的最大长度。
判断你是否能够到达最后一个下标，如果可以，返回 true ；否则，返回 false 。

示例 1：
输入：nums = [2,3,1,1,4]
输出：true
解释：可以先跳 1 步，从下标 0 到达下标 1, 然后再从下标 1 跳 3 步到达最后一个下标。
"""
class Solution:
    def canJump(self, nums: list[int]) -> bool:
        """
        
        :param nums:
        :return:
        """
        max_reach = 0
        for i, jump in enumerate(nums):
          if i > max_reach:
              return False
          max_reach=max(max_reach, i + jump)
        return True

if __name__ == '__main__':
    s=Solution()
    # print(s.canJump([2,3,1,1,4]))
    print(s.canJump([3,2,1,0,4]))