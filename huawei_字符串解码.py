"""
字符串解码
给定一个经过编码的字符串，返回它解码后的字符串。编码规则为: k[encoded_string]，表示其中方括号内部的 encoded_string 正好重复 k 次。
示例："3[a]2[bc]" -> "aaabcbc"
"""
def main(s : str)-> str:
    cnt=""
    stack = []
    for ch in s:
        tmp = ""
        # 1. 添加字符
        if ch != ']':
            stack.append(ch)
        # 2.处理[]中的字符
        else:
            while stack and stack[-1] != '[':
                tmp = stack.pop() + tmp
            stack.pop()

            # 3.处理[前的数字，可能出现双位数情况
            i = 1
            num =0
            while stack and stack[-1].isdigit():
                num = int(stack.pop()) * i +  num
                i *= 10
            cnt+= tmp * num

    return cnt

if __name__ == '__main__':
    print(main("[abcd]"))
    """
    数字是0；0[a]0[bc]
    纯字符串的；[abcd]
    双位数 13[a]2[bc]
    嵌套 1[ab2[cd]]
    """
