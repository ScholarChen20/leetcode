import sys

# for line in sys.stdin:
#     a = line.split()
#     print(int(a[0]) + int(a[1]))



def is_chongfu(s):
    """
    计算字符串的非重复子串的数量， 非重复字串的定义是每个字符出现的次数不超过一次
    例如 abaab 的非重复子串为ab ba ab 共三个，所以数量是3
    哈希map记录每个字符的次数，双指针，左指针为头 右指针为尾，下次开始的位置就是右指针加1
    """
    map = {}
    count = 0 # 非重复子串数量
    left = 0
    right = 0
    while right < len(s) and left <= right:
        if s[right] not in map:
            map[s[right]] = 1
            if right == len(s) - 1:
                count += 1
            right +=1
        else:
            map[s[right]] += 1
            right += 1
            while map[s[right-1]] > 1:
                map[s[left]] -= 1
                left += 1
            count += 1
    return count

def make_str(n, k):
    """
    n 表示这个字符串的长度，k表示这个字符串的奇异度（这个字符串的非重复字串的数量）
    返回满足以上条件的字符串（答案可以是多个）
    """



if __name__ == '__main__':
    # print(is_chongfu("abaab"))
    make_str(5, 3)