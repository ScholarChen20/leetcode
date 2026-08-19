"""
设计一个支持 push ，pop ，top 操作，并能在常数时间内检索到最小元素的栈。
实现 MinStack 类:
MinStack() 初始化堆栈对象。
void push(int value) 将元素 value 推入堆栈。
void pop() 删除堆栈顶部的元素。
int top() 获取堆栈顶部的元素。
int getMin() 获取堆栈中的最小元素。

示例 1:

输入：
["MinStack","push","push","push","getMin","pop","top","getMin"]
[[],[-2],[0],[-3],[],[],[],[]]

输出：
[null,null,null,null,-3,null,0,-2]
"""

class MinStack:

    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, value: int) -> None:
        self.stack.append(value)
        if not self.min_stack or value <= self.min_stack[-1]:
            self.min_stack.append(value)

    def pop(self) -> None:
        if self.stack:
            value = self.stack.pop()
            if value == self.min_stack[-1]:
                self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]

class MinStack1:
    def __init__(self):
        """
        initialize your data structure here. 栈中存储的是差值
        """
        self.stack = []
        self.min_value = -1

    def push(self, x: int) -> None:
        if not self.stack:
            self.stack.append(0)
            self.min_value = x
        else:
            diff = x-self.min_value
            self.stack.append(diff)
            self.min_value = self.min_value if diff > 0 else x

    def pop(self) -> None:
        if self.stack:
            diff = self.stack.pop()
            if diff < 0:
                top = self.min_value
                self.min_value = top - diff
            else:
                top = self.min_value + diff
            return top

    def top(self) -> int:
        return self.min_value if self.stack[-1] < 0 else self.stack[-1] + self.min_value

    def getMin(self) -> int:
        return self.min_value if self.stack else -1
