"""
小月得到一个由 0 和 1 组成的网格，行、列编号均从 1 开始。每次查询一个闭合子矩形，统计其中 1 的数量，并计算棋盘加权差值：
若格子坐标(i, j) 满足 (i + j) 为偶数，该格子中的 1 贡献 (+1)；若 (i + j) 为奇数则贡献 (-1)；字符 0 不贡献。

### 输入描述
第一行输入三个整数 \(n, m, q\) (\(1 \le n, m \le 300; 1 \le n \times m \le 10^5; 1 \le q \le 10^5\))，分别表示网格的行数、列数和查询次数。
此后 \(n\) 行，第 \(i\) 行输入一个长度为 \(m\)、只包含 0 和 1 的字符串，表示网格的第 \(i\) 行。
此后 \(q\) 行，第 \(i\) 行输入四个整数 \(r_{1i}, c_{1i}, r_{2i}, c_{2i}\) (\(1 \le r_{1i} \le r_{2i} \le n; 1 \le c_{1i} \le c_{2i} \le m\))，表示行号从 \(r_{1i}\) 到 \(r_{2i}\)、列号从 \(c_{1i}\) 到 \(c_{2i}\) 的子矩形。
### 输出描述
对于每次查询输出一行两个整数，依次表示子矩形中 1 的数量和棋盘加权差值。
### 示例 1

**输入**
3 4 3
1010
0111
0001
1 1 2 3
2 2 3 4

**输出**
4 2
4 0
6 2
"""


import sys
def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    n = int(input_data[0])
    m = int(input_data[1])
    q = int(input_data[2])

    grid = []
    idx = 3
    for _ in range(n):
        # 【修改点】不要用 int() 转换，保留字符串以支持按位读取字符
        grid.append(input_data[idx])
        idx += 1

    # 初始化前缀和数组
    pref_ones = [[0] * (m + 1) for _ in range(n + 1)]
    pref_weights = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        row_str = grid[i - 1]
        for j in range(1, m + 1):
            # 判断当前字符是否为 '1'
            is_one = 1 if row_str[j - 1] == '1' else 0

            weight = 0
            if is_one:
                if (i + j) % 2 == 0:
                    weight = 1
                else:
                    weight = -1

            # 容斥原理计算二维前缀和
            pref_ones[i][j] = pref_ones[i - 1][j] + pref_ones[i][j - 1] - pref_ones[i - 1][j - 1] + is_one
            pref_weights[i][j] = pref_weights[i - 1][j] + pref_weights[i][j - 1] - pref_weights[i - 1][j - 1] + weight

    results = []
    for _ in range(q):
        r1 = int(input_data[idx])
        c1 = int(input_data[idx + 1])
        r2 = int(input_data[idx + 2])
        c2 = int(input_data[idx + 3])
        idx += 4

        # 利用前缀和查询子矩形答案
        ans_ones = pref_ones[r2][c2] - pref_ones[r1 - 1][c2] - pref_ones[r2][c1 - 1] + pref_ones[r1 - 1][c1 - 1]
        ans_weight = pref_weights[r2][c2] - pref_weights[r1 - 1][c2] - pref_weights[r2][c1 - 1] + pref_weights[r1 - 1][
            c1 - 1]

        results.append(f"{ans_ones} {ans_weight}")

    sys.stdout.write('\n'.join(results) + '\n')


if __name__ == '__main__':
    solve()

    """
    核心思路是 **“二维前缀和（空间换时间）”**。

1. **为什么用？** 因为查询次数非常多（高达 \(10^5\)），如果每次查询都去挨个遍历子矩形里的格子，一定会超时（TLE）。我们需要把每次查询的时间降到最快。
2. **怎么做预处理？** 在读取数据时，建两个二维数组：一个记录格子中 `1` 的数量；另一个记录“加权值”（如果是 `1`，看坐标和的奇偶性记作 `+1` 或 `-1`）。把每个格子的值，都累加成“从左上角 `(1,1)` 到当前格子的总和”。
3. **怎么快速查询？** 对于任何给定的子矩形，不需要遍历，直接利用**容斥原理**（大矩形减去上方矩形，减去左方矩形，再加回多减的左上角矩形），通过四次简单的数组查询加减操作，就能直接算出答案。"""