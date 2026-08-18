"""
给定一个整数数组 temperatures ，表示每天的温度，返回一个数组 answer ，其中 answer[i] 是指对于第 i 天，下一个更高温度出现在几天后。如果气温在这之后都不会升高，请在该位置用 0 来代替。
示例 1:

输入: temperatures = [73,74,75,71,69,72,76,73]
输出: [1,1,4,2,1,1,0,0]
示例 2:

输入: temperatures = [30,40,50,60]
输出: [1,1,1,0]
"""

from typing import List
def dailyTemperatures(temperatures: List[int]) -> List[int]:
    stack =[]
    ans = [0] * len(temperatures)
    for i,t in enumerate(temperatures):
        while stack and t > temperatures[stack[-1]]:
            ans[stack[-1]] = i - stack[-1]
            stack.pop()
        stack.append(i)

    return ans

if __name__ == '__main__':
    print(dailyTemperatures([73,74,75,71,69,72,76,73]))
