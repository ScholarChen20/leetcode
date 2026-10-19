"""
n 个孩子站成一排。给你一个整数数组 ratings 表示每个孩子的评分。你需要按照以下要求，给这些孩子分发糖果：

每个孩子 至少 分配到 1 个糖果。
相邻两个孩子中，评分 更高 的那个会获得更多的糖果。
请你给每个孩子分发糖果，计算并返回需要准备的 最少 糖果数目。

示例 1：

输入：ratings = [1,0,2]
输出：5
解释：你可以分别给第一个、第二个、第三个孩子分发 2、1、2 颗糖果。
示例 2：

输入：ratings = [1,2,2]
输出：4
解释：你可以分别给第一个、第二个、第三个孩子分发 1、2、1 颗糖果。
     第三个孩子只得到 1 颗糖果，这满足题面中的两个条件。
"""
from typing import List
class Solution:
    def candy(self, ratings: List[int]) -> int:
        # 方法1：我们遍历该数组两次，处理出每一个学生分别满足左规则或右规则时，最少需要被分得的糖果数量。每个人最终分得的糖果数量即为这两个数量的最大值。
        n = len(ratings)
        left = [1] * n
        right = [1] * n
        for i in range(1,n):
            if ratings[i] > ratings[i - 1]:
                left[i] = left[i-1] + 1
        for i in range(n-2, -1, -1):
            if ratings[i] > ratings[i + 1]:
                right[i] = right[i+1] + 1

        ans = 0
        for i in range(n):
            ans += max(left[i], right[i])
        return ans

    def candy2(self, ratings: List[int]) -> int:
        # 方法2：我们只需要遍历该数组一次，即可得到最终的答案。具体地，我们用一个变量 left 记录当前学生左边学生的糖果数量，用一个变量 right 记录当前学生右边学生的糖果数量。在遍历的过程中，我们不断更新 left 和 right 的值，并根据 left 和 right 的值来更新当前学生的糖果数量。
        n = len(ratings)
        left = 1
        right = 1
        res = [1] * n
        for i in range(1,n):
            if ratings[i] > ratings[i-1]:
                left += 1
            else:
                left = 1
            res[i] = left
        for i in range(n-2,-1,-1):
            if ratings[i] > ratings[i+1]:
                right += 1
            else:
                right = 1
            res[i] = max(res[i], right)
        return sum(res)

if __name__ == '__main__':
    s = Solution()
    print(s.candy([1,0,2]))
    print(s.candy2([1,2,2]))

