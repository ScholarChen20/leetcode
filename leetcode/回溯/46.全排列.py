from typing import List

class Solution:
    def __init__(self):
        self.result = []
        self.cur = []

    def permute(self, nums: List[int]) -> List[List[int]]:
        n = len(nums)
        used = [False] * n

        def backtrack():
            if len(self.cur) == n:
                self.result.append(self.cur[:])
                return
            for i in range(n):
                if used[i]:
                    continue
                self.cur.append(nums[i])
                used[i] = True
                backtrack()
                self.cur.pop()
                used[i] = False

        backtrack()
        return self.result

if __name__ == '__main__':
    s = Solution()
    print(s.permute([1,2,3]))