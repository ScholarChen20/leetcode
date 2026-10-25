"""
给你一个字符串表达式 s ，请你实现一个基本计算器来计算并返回它的值。
注意:不允许使用任何将字符串作为数学表达式计算的内置函数，比如 eval() 。

示例 1：
输入：s = "1 + 1"
输出：2

示例 2：
输入：s = " 2-1 + 2 "
输出：3

示例 3：
输入：s = "(1+(4+5+2)-3)+(6+8)"
输出：23

示例4：
输入： s = "1-(     -2)"
输出：3
提示：
1 <= s.length <= 3 * 105
s 由数字、'+'、'-'、'('、')'、和 ' ' 组成
s 表示一个有效的表达式
'+' 不能用作一元运算(例如， "+1" 和 "+(2 + 3)" 无效)
'-' 可以用作一元运算(即 "-1" 和 "-(2 + 3)" 是有效的)
输入中不存在两个连续的操作符
每个数字和运行的计算将适合于一个有符号的 32位 整数
"""
class Solution:
    def calculate(self, s: str) -> int:
        st = [1]    # 符号栈，存放每一层的符号，一个括号表示一层；最顶层的符号为+1
        sign = 1    # 值为1或-1，表示当前数的符号
        n = len(s)
        i = 0
        res = 0
        while i < n:
            if s[i].isdigit():
                # 如果为数字，生成数值
                number = 0
                while i < n and s[i].isdigit():
                    number = number * 10 + int(s[i])
                    i += 1
                # 累加和，真实数字等于符号乘以数值
                res += sign * number
            else:
                if s[i] == '+':
                    sign = st[-1]   # 加号，获取当前层的符号
                elif s[i] == '-':
                    sign = -st[-1]  # 减号，获取当前层的相反符号
                elif s[i] == '(':
                    st.append(sign) # 左括号，进入新一层，将当前层符号入栈
                elif s[i] == ')':
                    st.pop()        # 右括号，完成一层的运算，弹出这一层符号
                i +=1   # 索引右移
        return res

if __name__ == '__main__':
    s = Solution()
    # print(s.calculate("(1+(4+5+2)-3)+(6+8)"))
    # print(s.calculate("2-1+2"))
    # print(s.calculate("1+(4+5+2)-3"))
    print(s.calculate("1-(-2)"))