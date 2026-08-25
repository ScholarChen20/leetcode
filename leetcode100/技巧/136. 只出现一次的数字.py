"""
给你一个 非空 整数数组 nums ，除了某个元素只出现一次以外，其余每个元素均出现两次。找出那个只出现了一次的元素。
你必须设计并实现线性时间复杂度的算法来解决此问题，且该算法只使用常量额外空间。

示例 1 ：
输入：nums = [2,2,1]
输出：1

示例 2 ：
输入：nums = [4,1,2,1,2]
输出：4

示例 3 ：
输入：nums = [1]
输出：1
"""
class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        """
        异或运算， 相同的数异或为0， 0异或任何数为任何数， 0^1^2^3^2^1 = 0^0^0^3 = 3
        & 运算，表示所有数的公共位， 1&1=1, 1&0=0, 0&1=0, 0&0=0
        | 运算，表示所有数的位或， 1|1=1, 1|0=1, 0|1=1, 0|0=0
        
        """
        res = 0
        ans = 1
        for num in nums:
            res ^= num
            ans &= num
        return res

if __name__ == '__main__':
    s = Solution()
    nums = list(map(int, input().split()))
    print(s.singleNumber(nums))