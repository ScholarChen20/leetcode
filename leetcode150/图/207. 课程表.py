"""
你这个学期必须选修 numCourses 门课程，记为 0 到 numCourses - 1 。
在选修某些课程之前需要一些先修课程。 先修课程按数组 prerequisites 给出，其中 prerequisites[i] = [ai, bi] ，表示如果要学习课程 ai 则 必须 先学习课程  bi 。
例如，先修课程对 [0, 1] 表示：想要学习课程 0 ，你需要先完成课程 1 。
请你判断是否可能完成所有课程的学习？如果可以，返回 true ；否则，返回 false 。

示例 1：

输入：numCourses = 2, prerequisites = [[1,0]]
输出：true
解释：总共有 2 门课程。学习课程 1 之前，你需要完成课程 0 。这是可能的。

输入：numCourses = 2, prerequisites = [[1,0],[0,1]]
输出：false
解释：总共有 2 门课程。学习课程 1 之前，你需要先完成​课程 0 ；并且学习课程 0 之前，你还应先完成课程 1 。这是不可能的。
"""
from typing import List
class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]):
        graph = [[] for _ in range(numCourses)] # 邻接表
        visited = [0] * numCourses # 0 未访问，1 已访问，-1 访问中
        for course,pre in prerequisites:
            graph[course].append(pre)

        def dfs(course, visited):
            if visited[course] == 1: # 已访问过，直接返回 True
                return True
            if visited[course] == -1:
                return False
            visited[course] = -1 # 标记为访问中
            for pre in graph[course]: # 递归遍历它的全部先修课；只要任一先修课路径上有环就立刻返回 False。
                if not dfs(pre, visited):
                    return False
            visited[course] = 1
            return True

        for course in range(numCourses):
            if not dfs(course, visited):
                return False
        return True

if __name__ == '__main__':
    numCourses = 2
    prerequisites = [[1,0], [0,1]]
    print(Solution().canFinish(numCourses, prerequisites))