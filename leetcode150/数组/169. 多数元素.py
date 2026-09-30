"""
给定一个大小为 n 的数组 nums ，返回其中的多数元素。多数元素是指在数组中出现次数 大于 ⌊ n/2 ⌋ 的元素。

你可以假设数组是非空的，并且给定的数组总是存在多数元素。

nums=[3,1,3]
输出： 1

nums = [2,2,1,1,1,2,2]
输出： 2
"""
from typing import List


def majorityElement(nums: List[int]) -> int:
    """
    摩尔投票 假设第一个元素和第二个元素相同 则记votes极为+2 否则为0 ,并且x即为一定即为多数元素的那个值 在一次遍历即可知道这个多数元素的个数并判断是否大于 【n/2]
    :param nums:
    :return:
    """
    votes, count = 0, 0
    for num in nums:
        if votes == 0: x = num
        votes += 1 if num == x else -1

    for num in nums:
        if num == x: count += 1
    return x if count > len(nums) / 2 else 0

if __name__ == '__main__':
    print(majorityElement(nums=[2,2,3]))
    # print(3 | 1 | 3)