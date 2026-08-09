def decodeString(s: str) -> str:
    """
    给定一个经过编码的字符串，返回它解码后的字符串。
    编码规则为: k[encoded_string]，表示其中方括号内部的 encoded_string 正好重复 k 次。注意 k 保证为正整数。
    你可以认为输入字符串总是有效的；输入字符串中没有额外的空格，且输入的方括号总是符合格式要求的。
    此外，你可以认为原始数据不包含数字，所有的数字只表示重复的次数 k ，例如不会出现像 3a 或 2[4] 的输入。
    输入：s = "3[a2[bc]]"
    输出：""
    """
    # 思路 栈＋递归
    stack = []
    cnt = ""
    for str in s:
        if str != ']':
            stack.append(str)
        else:
            tmp = ""
            while stack[-1] != '[':
                tmp = stack.pop() + tmp
            stack.pop()
            num = ""
            while stack and stack[-1].isdigit():
                num = stack.pop() + num
            ans = tmp * int(num)
            stack.append(ans)
    cnt = "".join(stack)
    return cnt

if __name__ == "__main__":
    s = "100[leetcode]"
    print(decodeString(s))



