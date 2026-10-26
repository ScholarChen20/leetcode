"""
定义二叉树的平衡路径需同时满足以下条件：
路径从任意节点出发，仅能向下延伸（只能向左/右子节点，不可向上回溯）
路径上所有节点的值相加为 0, 路径长度（包含的节点个数）至少为 2
输入二叉树的层序遍历列表（元素为整数或 None），返回该树中所有平衡路径的总数。

建树规则：层序遍历列表按从上到下、从左到右的顺序构建二叉树，None 表示对应位置无节点。路径只沿左子节点或右子节点单向向下（单链，不可分叉）。每个符合条件的单链路径独立计数。列表长度
≤10000≤10000，节点值范围 [−1000,1000]

样例
输入 [10, -5, -5, 2, -2, 3, -3]
输出 0

输入 [0, 0, None]
输出 1

输入 [1, -1, 2, -2, None, 3, -3]
输出 2
"""
import sys
from collections import defaultdict

sys.setrecursionlimit(20000)
input = sys.stdin.readline

line = input().strip()
start = line.index('[')
end = line.rindex(']')
content = line[start + 1:end]
tokens = content.split(',')

nodes = []
is_null = []
for t in tokens:
    t = t.strip()
    if t == 'None' or t == '':
        nodes.append(0)
        is_null.append(True)
    else:
        nodes.append(int(t))
        is_null.append(False)

n = len(nodes)
result = 0
counts = defaultdict(int)
counts[0] = 1

def dfs(idx, prefix_sum):
    global result
    if idx >= n or is_null[idx]: # 越界或空节点
        return
    prefix_sum += nodes[idx] # 当前节点值
    cnt = counts[prefix_sum] # 当前前缀和出现次数
    if nodes[idx] == 0: # 特殊处理
        cnt -= 1
    result += cnt # 更新结果
    counts[prefix_sum] += 1 # 更新前缀和计数
    dfs(2 * idx + 1, prefix_sum) # 左子树
    dfs(2 * idx + 2, prefix_sum) # 右子树
    counts[prefix_sum] -= 1 # 回溯

dfs(0, 0)
print(result)

"""
思路分析：层序二叉树中路径和为零的计数
本题的核心是在按层序排列的隐式二叉树中，高效统计节点数 >= 2 且路径和为 0 的路径数量。

隐式二叉树与前缀和
    输入数组即为层序遍历结果，索引 i 的左右孩子分别为 2i+1 和 2i+2，无需显式建树。从根节点向下遍历时，维护当前路径的前缀和 pre(v)。任意祖先 u 到后代 v 的路径和可表示为：路径和 = pre(v) - pre(u的父节点)。

哈希表优化查找
    路径和为 0 等价于 pre(v) = pre(u的父节点)。使用哈希表 counts 记录当前递归路径上各前缀和出现的次数。遍历到节点 v 时，counts[pre(v)] 的值即为以 v 结尾的零和路径数量。初始设置 counts[0] = 1，代表根节点上方的虚拟前缀和。

特殊处理与回溯
    长度约束：题目要求路径至少包含 2 个节点。若当前节点值为 0，会导致 pre(v) 等于父节点前缀和，从而错误匹配到“单节点路径”。此时需将查询结果减 1。
    回溯机制：采用 DFS 遍历，进入子树前将当前前缀和加入哈希表，退出子树后必须将其移除（计数减 1），防止左子树的数据干扰右子树的查询。
"""