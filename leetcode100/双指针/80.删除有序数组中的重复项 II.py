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
        """快慢指针法, 思路：快指针遍历数组，慢指针记录新数组的长度，如果快指针指向的元素和慢指针指向的元素不相等，则将快指针指向的元素赋值给慢指针指向的元素，然后慢指针+1，最后返回慢指针的值
        时间复杂度O(n)，空间复杂度O(1)"""
        slow = fast = 2
        n = len(nums)
        if n <= 2:
            return 2

        while fast<n: # 快指针遍历数组
            if nums[slow-2] != nums[fast]:
                nums[slow] = nums[fast]
                slow += 1
            fast += 1
        return slow

    def removeDuplicates2(self, nums: List[int]):
        """
        哈希表法，思路：用哈希表记录每个元素出现的次数，然后遍历数组，如果当前元素出现的次数小于等于2，则将当前元素赋值给慢指针指向的元素，然后慢指针+1，最后返回慢指针的值
        时间复杂度O(n)，空间复杂度O(n)
        """
        n = len(nums)
        if n <= 2:
            return 2

        count = {} # 哈希表记录每个元素出现的次数
        slow = 0
        for i in range(n):
            if nums[i] not in count:
                count[nums[i]] = 1
            else:
                count[nums[i]] += 1
            if count[nums[i]] <= 2:
                nums[slow] = nums[i]
                slow += 1
        return slow

if __name__ == '__main__':
    m = Solution()
    print(m.removeDuplicates(nums=[1,1,1,2,2,3]))
