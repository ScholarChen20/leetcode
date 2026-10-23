"""
实现 pow(x, n) ，即计算 x 的整数 n 次幂函数（即，xn ）。

示例 1：

输入：x = 2.00000, n = 10
输出：1024.00000
示例 2：

输入：x = 2.10000, n = 3
输出：9.26100
示例 3：

输入：x = 2.00000, n = -2
输出：0.25000
解释：2-2 = 1/22 = 1/4 = 0.25
"""
class Solution:
    def myPow(self, x: float, n: int) -> float:
        """快速幂"""
        if n < 0:
            x = 1 / x
            n = -n
        res = 1
        while n > 0:
            if n & 1:
                res *= x
            x *= x
            n >>= 1 # 右移一位，相当于除以2
        return res

    def myPow(self, x: float, n: int) -> float:
        """递归"""
        if n == 0:
            return 1
        if n < 0:
            x = 1 / x
            n = -n
        return self.myPow(x * x, n // 2) if n % 2 == 0 else x * self.myPow(x * x, n // 2)



if __name__ == '__main__':
    # print(Solution().myPow(2.00000, 10))
    print(Solution().myPow(2.10000, 3))