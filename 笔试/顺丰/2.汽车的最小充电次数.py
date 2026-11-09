"""
我们需要从起点（位置 0 ）出发，到达终点（位置 L ）。汽车初始有 startFuel 升油，每升油行驶 1 单位距离。途中有 n 个加油站，第 i 个加油站在位置 a_i，可以加 b_i
升油。加油站按位置严格递增排列（0<a1<a2<...<an<L) 。目标：到达终点时，加油次数尽可能少。如果无法到达终点，输出 −1 。

【示例】：
输入：
3
12 4 3
2 5
5 3
8 6
10 15 2
3 2
7 1
5 2 0

输出：
2
0
-1
"""
import heapq
def solve():
    t = int(input())
    for _ in range(t):
        L, startFuel, n = map(int, input().split())
        if n == 0:
            print(1 if startFuel >= L else -1)
            continue


        stations = [[0, 0] for _ in range(n)]
        for i in range(n):
            stations[i][0], stations[i][1] = map(int, input().split())

        # 定义一个最大堆（存负值）
        queue = []
        currentFuel = startFuel
        currentPosition = 0
        ans = 0
        for i in range(n + 1):
            target = L if i == n else stations[i][0]
            dist = target - currentPosition

            while currentFuel < dist and queue is not None:
                fuel = -heapq.heappop(queue)
                currentFuel += fuel
                ans += 1

            if currentFuel < dist:
                ans -= 1
                break

            currentFuel -= dist
            currentPosition = target

            if i < n:
                heapq.heappush(queue, -stations[i][1])

        print(ans)

if __name__ == '__main__':
    solve()


