"""
给定一个整数 n，返回 n! 结果尾数中零的数量。
提示 n! = n * (n - 1) * (n - 2) * ... * 3 * 2 * 1

示例 1：

输入：n = 3
输出：0
解释：3! = 6 ，不含尾随 0
示例 2：

输入：n = 5
输出：1
解释：5! = 120 ，有一个尾随 0
示例 3：

输入：n = 0
输出：0
"""
class Solution:
    """n! 尾零的数量即为 n! 中因子 10 的个数，而 10=2×5，因此转换成求 n! 中质因子 2 的个数和质因子 5 的个数的较小值。

由于质因子 5 的个数不会大于质因子 2 的个数（具体证明见方法二），我们可以仅考虑质因子 5 的个数。

而 n! 中质因子 5 的个数等于 [1,n] 的每个数的质因子 5 的个数之和，我们可以通过遍历 [1,n] 的所有 5 的倍数求出。"""
    def trailingZeroes(self, n: int) -> int:
        """统计5的个数"""
        res = 0
        while n > 0:
            n //= 5
            res += n
        return res

class Solution1:
    def trailingZeroes(self, n: int) -> int:
        ans = 0
        for i in range(5, n + 1, 5):
            while i % 5 == 0:
                i //= 5
                ans += 1
        return ans


if __name__ == '__main__':
    print(Solution().trailingZeroes(5))
    print(Solution().trailingZeroes(10))
