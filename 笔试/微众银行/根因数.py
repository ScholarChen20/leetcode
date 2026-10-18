"""
以下是为您提取并整理为 Markdown 格式的题目要求和示例：

### 题目描述

我们定义，如果一个数字可以表示为 \(x=2^a*5^b\)，那么我们称这个数字 \(x\) 为根因数。现在给你 \(q\) 次询问，每次询问一个区间 \(l\) 到 \(r\)，请你计算区间内有多少个根因数。

### 输入描述

第一行一个整数 \(q(1 \le q \le 10^5)\)，代表询问的总数。
接下来 \(q\) 行，每行两个整数 \(l(1 \le l)\) 和 \(r(r \le 10^{17})\)，代表询问的区间。

### 输出描述

对于每组询问，一行一个整数代表询问区间内根因数的数量。

### 样例输入

```text
3
1 10
1 100
123456789 1234567890
```

### 样例输出

```text
6
15
44
```

### 提示

对于第一组询问，合法的数字有六个，分别为 1, 2, 4, 5, 8, 10。
"""

import sys
from bisect import bisect_left, bisect_right # 二分查找
def generate_root_numbers(limit):
    """生成所有小于等于 limit 的根因数"""
    roots = set()
    # 2^a
    p2 = 1
    while p2 <= limit:
        # 5^b
        p5 = 1
        while p2 * p5 <= limit:
            roots.add(p2 * p5)
            p5 *= 5
        p2 *= 2
    # 转为排序后的列表，方便二分查找
    return sorted(list(roots))


def solve():
    # 设置上限为 10^17
    MAX_LIMIT = 10 ** 17

    # 1. 预处理生成所有根因数
    root_numbers = generate_root_numbers(MAX_LIMIT)

    # 2. 读取输入,使用 sys.stdin.read() 可以快速读取所有输入，应对大数据量
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    q = int(input_data[0])
    results = []

    # 3. 处理每次查询
    idx = 1
    for _ in range(q):
        l = int(input_data[idx])
        r = int(input_data[idx + 1])
        idx += 2

        # 使用二分查找寻找区间内的数量
        left_pos = bisect_left(root_numbers, l) # bisect_left 找到第一个 >= l 的位置
        right_pos = bisect_right(root_numbers, r) # bisect_right 找到第一个 > r 的位置

        results.append(str(right_pos - left_pos)) # 两者相减即为 [l, r] 之间的元素个数

    # 4. 输出结果
    print('\n'.join(results))


if __name__ == '__main__':
    solve()