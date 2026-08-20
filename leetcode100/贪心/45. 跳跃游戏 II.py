"""
45. 跳跃游戏 II
给定一个长度为 n 的 0 索引整数数组 nums。初始位置在下标 0。

每个元素 nums[i] 表示从索引 i 向后跳转的最大长度。换句话说，如果你在索引 i 处，你可以跳转到任意 (i + j) 处：
0 <= j <= nums[i] 且
i + j < n
返回到达 n - 1 的最小跳跃次数。测试用例保证可以到达 n - 1。

示例 1:
输入: nums = [2,3,1,1,4]
输出: 2
解释: 跳到最后一个位置的最小跳跃数是 2。
     从下标为 0 跳到下标为 1 的位置，跳 1 步，然后跳 3 步到达数组的最后一个位置。

输入: nums = [2,3,0,1,4]
输出: 2
"""
class Solution:
    def jump(self, nums: list[int]) -> int:
        """
        贪心算法，jumps表示跳跃次数，current_head表示当前能到达的最远距离，next_head表示下一步能到达的最远距离
        """
        jumps = 0 # 跳跃次数
        current_head = 0    # 当前能到达的最远距离
        next_head = 0        # 下一步能到达的最远距离
        for i ,jump in enumerate(nums):
            if i > current_head: # 如果i > current_head，则需要跳跃一次，更新current_head为next_head
                jumps += 1
                current_head = next_head
            next_head = max(next_head, i + jump)
        return jumps

if __name__ == '__main__':
    s=Solution()
    print(s.jump([2,3,1,1,4]))