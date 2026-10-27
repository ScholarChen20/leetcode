"""
给你一个整数数组 nums ，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k ，同时还满足 nums[i] + nums[j] + nums[k] == 0 。请你返回所有和为 0 且不重复的三元组。
注意：答案中不可以包含重复的三元组。
示例 1:
输入：nums = [-1,0,1,2,-1,-4]
输出：[[-1,-1,2],[-1,0,1]]
解释：
nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0 。
nums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0 。
nums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0 。

示例 2：
输入：nums = [0,1,1]
输出：[]
解释：唯一可能的三元组和不为 0 。
"""
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        """
        三指针法, 思路：先排序，然后固定一个数，然后用双指针法找到另外两个数，然后判断三数之和是否为0，如果为0，则将这三个数加入到结果中，然后移动左右指针，直到左右指针相遇，然后固定下一个数，重复上述过程，直到固定数遍历完整个数组
        """
        n = len(nums)
        res = []
        nums.sort()

        for k in range(n - 2):
            i, j = k + 1, n - 1
            while i < j:
                total = nums[i] + nums[j] + nums[k]
                if total == 0:
                    res.append([nums[k], nums[i], nums[j]])
                    while nums[i] == nums[i + 1] and i < j:
                        i += 1
                    while nums[j] == nums[j-1] and j > i:
                        j -= 1
                    i += 1
                    j -= 1
                elif total < 0:
                    i += 1
                else:
                    j -= 1
        return res


if __name__ == '__main__':
    s = Solution()
    print(s.threeSum([-1,0,1,2,-1,-4]))