"""
给定一个非空整数数组，除了某个元素只出现一次以外，其余每个元素均出现三次。找出那个只出现了一次的元素。

示例1：
输入：[2,2,3,2]
输出：3
示例2：
输入：[0,1,0,1,0,1,99]
输出：99
"""
from typing import List
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        # 每一位分别数 1 → 对 3 取余，消掉出现三次的数字 → 用剩余的位还原答案。
        ans = 0
        for i in range(32):
            total = sum((num >> i) & 1 for num in nums) # num >> i 把第 i 位移到最右边，& 1 只取最右边这一位，所以结果是 0 或 1
            if total % 3:
                # Python 这里对于最高位需要特殊判断
                if i == 31:
                    ans -= (1 << i)
                else:
                    ans |= (1 << i)
        return ans

if __name__ == '__main__':
    print(Solution().singleNumber([2,2,3,2]))