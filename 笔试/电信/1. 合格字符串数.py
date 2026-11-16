"""
你需要处理一个由小写字母和 # 组成的字符串。# 作为分隔符，将字符串切分成若干个标签（标签非空）。
对于每一个标签，必须同时满足以下三个条件才算“合格”：首尾字符不同：tag.charAt(0) != tag.charAt(tag.length() - 1)。
元音数量为奇数：统计 a, e, i, o, u 出现的总次数，该次数必须是奇数。不同字符数量至少为 3：标签内部出现过的不同字母种类数≥3。
输出要求：
第一项：合格标签的总数。
第二项：所有合格标签的长度总和。
第三项：合格标签中的最大长度。
特殊注意：如果没有合格标签，第二项和第三项均输出 0。

示例 1:
输入: bca#dog
输出： 2 6 3

示例 2:
输入: abc#bbb
输出： 1 3 3
"""
def solve():
    # 读取输入，并去除可能存在的首尾空白字符
    s = input().strip()
    tags = s.split('#')

    # 初始化统计变量
    valid_count = 0  # 合格标签数量
    total_length = 0  # 合格标签总长度
    max_length = 0  # 合格标签最大长度

    # 元音字母集合（用于加速判断）
    vowels = set('aeiou')

    for tag in tags:
        # 防御性判断：忽略空字符串
        if not tag:
            continue

        # 条件1：首尾字符不同
        condition1 = (tag[0] != tag[-1])

        # 条件2：元音字母数量为奇数
        # 使用 sum 和生成器表达式统计元音数量
        vowel_count = sum(1 for char in tag if char in vowels)
        condition2 = (vowel_count % 2 != 0)

        # 条件3：不同字符数量至少为 3
        # 使用 set() 去重，然后看长度是否大于等于 3
        condition3 = (len(set(tag)) >= 3)

        # 如果三个条件同时满足，则该标签合格
        if condition1 and condition2 and condition3:
            valid_count += 1
            tag_len = len(tag)
            total_length += tag_len
            # 更新最大长度
            if tag_len > max_length:
                max_length = tag_len

    # 按照题目要求输出结果
    # 如果不存在合格标签，输出 "0 0 0"
    if valid_count == 0:
        print("0 0 0")
    else:
        print(f"{valid_count} {total_length} {max_length}")


if __name__ == "__main__":
    solve()