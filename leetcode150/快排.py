import random


def quick_sort(nums: list): # 简捷递归版
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    left = [x for x in nums if x < pivot]
    middle = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def quick_sort_range(nums: list, low=0, high=None):
    if high is None:
        high = len(nums) - 1
    if low < high:
        pi = partition(nums, low, high)
        quick_sort_range(nums, low, pi - 1)
        quick_sort_range(nums, pi + 1, high)
    return nums

def partition(arr, low, high):
    pivot = arr[high]  # 选最后一个元素做 pivot
    # pivot = random.choice(arr[low:high + 1])
    i = low -1 # i 是"≤ pivot 区域"的右边界，初始为空
    for j in range(low, high):
        if arr[j] < pivot:  # 遇到小的放左半区
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    # 循环结束后：[low..i] 都 ≤ pivot，[i+1..high-1] 都 > pivot
    arr[i + 1], arr[high] = arr[high], arr[i + 1] # 把 pivot 放到分界点
    return i + 1

if __name__ == '__main__':
    print(quick_sort_range([3,7,5,1,2,1], 0, None))