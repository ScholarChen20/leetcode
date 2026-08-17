""""
给你一个有序数组 nums ，请你 原地 删除重复出现的元素，使得出现次数超过两次的元素只出现两次 ，返回删除后数组的新长度。

不要使用额外的数组空间，你必须在 原地 修改输入数组 并在使用 O(1) 额外空间的条件下完成。

输入：nums = [1,1,1,2,2,3]
输出：5, nums = [1,1,2,2,3]
解释：函数应返回新长度 length = 5, 并且原数组的前五个元素被修改为 1, 1, 2, 2, 3。 不需要考虑数组中超出新长度后面的元素。
"""
from typing import List
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        slow=fast=2
        n=len(nums)
        if n <= 2:
            return 2

        while fast<n:
            if nums[slow-2]!=nums[fast]:
                nums[slow]=nums[fast]
                slow+=1
            fast+=1
        return slow
if __name__ == '__main__':
    m = Solution()
    print(m.removeDuplicates(nums=[1,1,1,2,2,3]))
