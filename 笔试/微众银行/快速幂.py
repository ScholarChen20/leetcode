"""
你在探索过程中遇到一个六位密码箱，旁边放着一张纸条，上面写着有关密码的提示，内容如下：数字 123456，对于其所有可能的排列，计算其 p 次幂结果的后六位，其中最大的那一个即为密码。数字 p 的值写在了纸条的背面。
于是你翻开了纸条的背面...
注意，123456 的排列可以理解为随意打乱各个数位得到一个新的数字，例如 312465，461253 是 123456 的排列，而 221435 不是，因为 2 出现了两次，6 没有出现。

【输入】：
p 的值，一个整数，1 ≤ p ≤ 1000000000
【输出】：
密码，一个六位数，前导零补齐

示例：
输入：2
输出：998144   （排列为 364512，其二次幂的结果为 132868998144，后六位为 998144，是所有排列的二次幂后六位中最大的。）
"""

import itertools  # 用于生成 1 到 6 的所有全排列
def solve():
    # 读取输入的 p
    # 如果是在实际判题系统中，可以直接用 p = int(input())
    p_str = input("请输入 p 的值: ").strip()
    if not p_str:
        return
    p = int(p_str)

    MOD = 1000000
    max_result = -1

    # 生成 1 到 6 的所有全排列
    digits = "123456"
    permutations = itertools.permutations(digits)

    for perm in permutations:
        # 将排列元组转换为整数
        num = int("".join(perm))

        # 计算 num 的 p 次方，并对 10^6 取模
        # Python 内置的 pow(base, exp, mod) 函数本身就是高效的快速幂实现
        # 避免将巨大的数字完整算出来再取模导致内存溢出或超时
        res = pow(num, p, MOD)

        # 更新最大值
        if res > max_result:
            max_result = res

    # 输出结果，注意题目要求：如果小于 6 位数，需要用前导零补齐 (例如 zfill(6))
    print(str(max_result).zfill(6))


if __name__ == "__main__":
    solve()
