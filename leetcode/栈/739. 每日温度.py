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
