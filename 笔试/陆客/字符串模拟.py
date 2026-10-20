"""
题目要求我们对一个字符串 s 进行一系列操作。给定字符串长度 n 和整数 k ，我们需要依次对 i=1,2,…,n−k+1 执行以下操作：
将当前字符串中从第 i 个字符到第 i+k−1 个字符（即长度为 k 的连续子串）进行反转。
最终输出经过所有操作后的字符串。

示例：
输入： 5 3
hello
输出： lloeh

输入： 8 5
nowcoder
输出： odernowc
"""


import sys
from collections import deque
# 设置递归深度和读取方式，防止大数据量出错
sys.setrecursionlimit(200000)
input = sys.stdin.read
def solve():
    data = input().split()
    if not data:
        return

    n = int(data[0])
    k = int(data[1])
    s = data[2]

    # 特殊情况：如果 k=1，反转长度为1的串等于没反转
    if k == 1:
        print(s)
        return

    # 修正规律：
    # 将字符串分为 A (前 k-1 个) 和 B (剩下的)。
    # 结果是 B + reverse(A) 吗？
    # hello: A='he', B='llo'. B + rev(A) = 'llo' + 'eh' = 'lloeh'. (匹配！)
    # nowcoder: A='nowc', B='oder'. B + rev(A) = 'oder' + 'cwon' = 'odercwon'.
    # 预期是 'odernowc'. (不匹配！A没有反转)

    # 为什么 hello 反转了，nowcoder 没反转？
    # hello: n=5, k=3. 操作次数 = 5-3+1 = 3次。 (奇数次)
    # nowcoder: n=8, k=5. 操作次数 = 8-5+1 = 4次。 (偶数次)

    # 假设规律：
    # 1. 分割点为 k-1。
    # 2. 后半部分 s[k-1:] 保持不变，放到最前面。
    # 3. 前半部分 s[:k-1] 放到最后面。
    # 4. 如果操作次数 (n-k+1) 是奇数，则前半部分需要反转；如果是偶数，则不反转。

    ops = n - k + 1
    part_a = s[: k -1]
    part_b = s[ k -1:]

    if ops % 2 == 1:
        part_a = part_a[::-1]

    print(part_b + part_a)

if __name__ == '__main__':
    solve()
