"""
给定一个包含红色、白色和蓝色、共 n 个元素的数组 nums ，原地 对它们进行排序，使得相同颜色的元素相邻，并按照红色、白色、蓝色顺序排列。
我们使用整数 0、 1 和 2 分别表示红色、白色和蓝色。
必须在不使用库内置的 sort 函数的情况下解决这个问题。

示例 1：

输入：nums = [2,0,2,1,1,0]
输出：[0,0,1,1,2,2]

示例 2：

输入：nums = [2,0,1]
输出：[0,1,2]
"""
class Solution:
    def sortColors(self, nums: list[int]) -> None:
        """
        双指针，p0指向0的最右边， p2指向2的最左边， cur指向当前元素， 如果cur是0， 则与p0交换， p0++， cur++， 如果cur是2， 则与p2交换， p2--， 如果cur是1， 则cur++
        """
        n = len(nums)
        p0, p2 = 0, n - 1
        cur = 0
        while cur <= p2:
            if nums[cur] == 0: #
                nums[cur], nums[p0] = nums[p0], nums[cur]
                p0 += 1
                cur += 1
            elif nums[cur] == 2:
                nums[cur], nums[p2] = nums[p2], nums[cur]
                p2 -= 1
            else:
                cur += 1

if __name__ == '__main__':
    s = Solution()
    nums = list(map(int, input().split()))
    s.sortColors(nums)
    print(nums)