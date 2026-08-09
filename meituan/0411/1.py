import sys

def main():
    # 读取第一行的n
    t = int(sys.stdin.readline().strip())
    for i in range(t):
        # 读取每一行
        line = sys.stdin.readline().strip()
        # 把每一行的数字分隔后转化成int列表
        values = list(map(int, line.split()))
        n = values[0]
        x = values[1]

        # 读取下一行
        line = sys.stdin.readline().strip()
        values = list(map(int, line.split()))
        print(is_valid(values, n, x))


def is_valid(arr, n , x):
    # 数组arr按顺序两两元素成盒，例如1 2 3 4，则两两元素成盒为[1,2] [3,4]
    items = []
    for i in range(0, n-1, 2):
        items.append([arr[i], arr[i+1]])
        if i+1 == n-2:
            items.append([arr[i+2]])

    arr_num = len(items)
    if arr_num < x:
        return "No"

    must_odd = 0
    can_odd = 0

    # 遍历items的每个数组元素a,b
    for i in range(arr_num):
        list = items[i]
        a = list[0]
        b = list[1] if len(list) > 1 else 0
        if a % 2 == 1 and b % 2 == 1 and b != 0:
            must_odd += 1
        elif a % 2 == 1 or b % 2 == 1:
            can_odd += 1

    min_odd = min(must_odd, x)
    max_odd = min(must_odd+can_odd, x)

    return "Yes" if any(k%2 == 1 for k in range(min_odd, max_odd+1)) else "No"

if __name__ == '__main__':
    main()