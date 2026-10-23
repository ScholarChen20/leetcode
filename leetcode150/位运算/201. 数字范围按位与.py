"""
给你两个整数 left 和 right ，表示区间 [left, right] ，返回此区间内所有数字 按位与 的结果（包含 left 、right 端点）。
示例 1：

输入：left = 5, right = 7
输出：4
示例 2：

输入：left = 0, right = 0
输出：0
示例 3：

输入：left = 1, right = 2147483647
输出：0
"""
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        """位运算: 从高到低遍历，如果left和right的第i位不同，则第i位为0，否则为1"""
        res = 0
        for i in range(31, -1, -1):
            if (left & (1 << i)) != (right & (1 << i)):
                break
            res |= (left & (1 << i))
        return res

if __name__ == '__main__':
    print(Solution().rangeBitwiseAnd(5, 7))