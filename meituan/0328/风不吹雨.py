import sys

def solve():
    # 使用 buffer 读取所有输入，速度最快
    input_data = sys.stdin.buffer.read().split()
    if not input_data:
        return

    # 使用迭代器逐个获取数据
    iterator = iter(input_data)

    try:
        # 读取测试用例组数 T
        t = int(next(iterator))

        results = []

        for _ in range(t):
            # 读取 n, a, b, k
            n = int(next(iterator))
            a = int(next(iterator))
            b = int(next(iterator))
            k = int(next(iterator))

            # 读取数组元素
            arr = []
            current_sum = 0
            gains = []

            for _ in range(n):
                val = int(next(iterator))
                arr.append(val)
                current_sum += val

                # 计算对当前数值执行操作1的收益
                # 操作1：val -> val // 2
                # 收益 = val - (val // 2)
                # 对于正整数，这等价于 (val + 1) // 2
                gain = val - (val // 2)
                gains.append(gain)

            # 贪心策略：
            # 1. 优先执行收益最大的操作1。
            # 将收益从大到小排序
            gains.sort(reverse=True)

            # 选取前 a 个最大的收益进行扣除
            # 注意：如果 a > n，循环会自动处理（因为切片不会越界，或者我们在循环中限制范围）
            for i in range(min(a, n)):
                current_sum -= gains[i]

            # 2. 执行操作2。
            # 操作2每次固定减少 k，共执行 b 次
            current_sum -= b * k

            results.append(str(current_sum))

        # 一次性输出所有结果，用换行符连接
        sys.stdout.write("\n".join(results))

    except StopIteration:
        pass


if __name__ == '__main__':
    # solve()
    import sys

    # b, a = map(int, sys.stdin.readline().strip().split(' '))
    tmp = list(map(int, sys.stdin.readline().strip().split(' ')))

    print(tmp)