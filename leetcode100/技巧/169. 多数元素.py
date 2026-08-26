"""
给定一个大小为 n 的数组 nums ，返回其中的多数元素。多数元素是指在数组中出现次数 大于 ⌊ n/2 ⌋ 的元素。
你可以假设数组是非空的，并且给定的数组总是存在多数元素。进阶：尝试设计时间复杂度为 O(n)、空间复杂度为 O(1) 的算法解决此问题。

示例 1：
输入：nums = [3,2,3]
输出：3
示例 2：

输入：nums = [2,2,1,1,1,2,2]
输出：2
"""
import collections
class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        """
        摩尔投票法， 设定一个候选人和一个计数器， 遍历数组， 如果计数器为0， 则将当前元素设为候选人， 如果当前元素等于候选人， 则计数器加1， 否则计数器减1， 最后返回候选人
        """
        count = 0
        candidate = None
        for num in nums:
            if count == 0:
                candidate = num
            count += (1 if num == candidate else -1)
        return candidate

    def majorityElement_sort(self, nums: list[int]) -> int:
        """
        排序法， 排序后， 中间的元素就是多数元素。 时间复杂度O(nlogn)
        """
        nums.sort()
        return nums[len(nums) // 2]

    def majorityElement_hash(self, nums: list[int]) -> int:
        """
        哈希表法， 遍历数组， 统计每个元素的出现次数， 如果出现次数大于n/2， 则返回该元素。 时间复杂度O(n)， 空间复杂度O(n)
        """
        count = collections.Counter(nums)
        for num, cnt in count.items():
            if cnt > len(nums) // 2:
                return num

if __name__ == '__main__':
    s = Solution()
    nums = list(map(int, input().split()))
    print(s.majorityElement(nums))

