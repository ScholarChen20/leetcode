"""
题目描述了 n 个养鸡场，每个养鸡场初始有 a[i] 只小鸡。每天每个养鸡场都会增加 k 只小鸡。在每天结束时，需要找出小鸡数量最多的养鸡场（如果有多个，任选一个），将其小鸡数量减半（向下取整，即 ⌊x/2⌋ ）。我们需要计算 m 天后所有养鸡场的小鸡总数。
输入范围：
1≤m≤100000 （天数）
1≤n≤100000 （养鸡场数量）
1≤k≤10000 （每天每个场增加的小鸡数）
1≤a[i]≤100000 （初始小鸡数）
核心操作：
每天所有养鸡场的小鸡数先统一增加 k 。
找出当前最大值 x ，将其更新为 ⌊x/2⌋ 。
重复 m 天，最后求总和。

输入：
3 3 100
100 200 400
输出： 925
"""

import heapq
def solve():
    n, m, k = map(int, input().split())
    a = list(map(int, input().split()))

    # Python 的 heapq 是最小堆，我们存负数来模拟最大堆
    pq = []
    for x in a:
        heapq.heappush(pq, -x)

    current_add = 0
    for _ in range(m):
        current_add += k
        max_val_stored = -heapq.heappop(pq)         # 取出最大值（负数）
        max_val_actual = max_val_stored + current_add

        half_actual = max_val_actual // 2
        new_stored = half_actual - current_add

        heapq.heappush(pq, -new_stored)

    total_stored = 0
    while pq:
        total_stored += -heapq.heappop(pq)

    ans = total_stored + n * current_add
    print(ans)

if __name__ == '__main__':
    solve()