"""
题目分析
我们需要在数组 A （长度为 n ）中找到一个最短的连续区间 [l,r] ，使得对于所有 1≤x≤m 的正整数 x ，数字 x 在区间 [l,r] 中出现的次数至少为 b
x次（ bx是数组 B 中第 x 个数）。



输入：
8 5
2 3 3 1 2 4 2 5
1 2 0 0 0
输出：4
"""

# 这是一个典型的“滑动窗口”（双指针）问题。我们需要维护一个区间 [l,r] ，并动态统计区间内每个数字的出现次数，同时判断是否满足所有 bx的要求。
import sys
def solve():
    n, m = map(int, sys.stdin.readline().split())
    A = list(map(int, sys.stdin.readline().split()))
    B = list(map(int, sys.stdin.readline().split()))

    need = [0] * (m + 1)
    total_needed = 0
    for i in range(1, m + 1):
        need[i] = B[i - 1]
        if need[i] > 0:
            total_needed += 1

    cnt = [0] * (max(m, max(A)) + 1 if A else m + 1)
    current_satisfied = 0
    min_len = float('inf')
    left = 0

    for right in range(n):
        val = A[right]
        if val <= m:
            cnt[val] += 1
            if cnt[val] == need[val]:
                current_satisfied += 1

        while current_satisfied == total_needed:
            min_len = min(min_len, right - left + 1)
            left_val = A[left]
            if left_val <= m:
                if cnt[left_val] == need[left_val]:
                    current_satisfied -= 1
                cnt[left_val] -= 1
            else:
                cnt[left_val] -= 1  # 虽不用判断，但保持计数一致
            left += 1

    print(min_len if min_len != float('inf') else -1)

if __name__ == '__main__':
    solve()