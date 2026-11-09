"""
纸片初始：高 h，宽 w
切割规则（**只能二选一平分**）：

1. 若 w 是偶数：沿宽切，分成两片 (h, w/2)
2. 若 h 是偶数：沿高切，分成两片 (h/2, w)
每切一刀，一片变两片；**每一片都可以独立继续切**，只要它自己的 h 或者 w 为偶数。
问：最多能切出多少片？能不能≥n？

【示例】：
输入：（第一个数字t表示测试数据数，剩下t行的w_i,h_i,n_i表示第i行的长、宽以及别切至少的数量卡片
5
3 3 2
2 2 3
3 10 2
1 1 1
1 4 4

输出：
NO
YES
YES
YES
YES
"""
def count_two(x):
    cnt = 0
    while x % 2 == 0:
        cnt += 1
        x //= 2
    return cnt

def solve():
    t = int(input())
    for _ in range(t):
        w, h, n = map(int, input().split())
        wi = count_two(w)
        hi = count_two(h)
        cnt = 2 ** (wi + hi)
        if cnt >= n:
            print("YES")
        else:
            print("NO")

if __name__ == '__main__':
    solve()
