from typing import List


def jump(self, nums: List[int]) -> int:
    n = len(nums)
    flag = List[int]
    for num in nums:
        for i in range(num):
            flag.append(1)
