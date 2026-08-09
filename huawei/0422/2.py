"""
输出：
[10, -5, -5, 2, -2, 3, -3]
输出：0
[0, 0, None]
输出：1
"""
import sys
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
def build_tree(level_order): # 层序遍历
    if not level_order or len(level_order) == 0:
        return None
    root = TreeNode(level_order[0])
    queue = [root]
    i = 1
    n = len(level_order)
    while i < len(level_order):
        node = queue.pop(0)
        if i < n and level_order[i] is not None:
            node.left = TreeNode(level_order[i])
            queue.append(node.left)
        i += 1
        if i < n and level_order[i] is not None:
            node.right = TreeNode(level_order[i])
            queue.append(node.right)
        i += 1
    return root

def count_balanced_subtrees(node): # 平衡路径定义是从任意一节点出发，向下延伸（左、右节点）路径上所有节点累加和为0 且路径长度>=2, 返回平衡路径的数量
    count = 0
    def dfs(node, sum, path_len):
        nonlocal count
        if node is None :
            return 0
        current_sum = sum + node.val
        current_length  = path_len + 1
        if current_sum == 0 and current_length >= 2:
            count += 1
        dfs(node.left, current_sum, current_length)
        dfs(node.right, current_sum, current_length)
    def traverse(node):
        if node is None:
            return
        dfs(node, 0, 0)
        traverse(node.left)
        traverse(node.right)
    traverse(node)
    return count

def main():
    # 输入列表 []类似格式，自定义输入
    # level_order = [x for x in input().strip().split(',')]
    # # 去除第一个元素和最后一个元素的[和]
    # first = level_order[0]
    # last = level_order[-1]
    # first = first[1:]
    # last = last[:-1]
    # level_order[0] = first
    # level_order[-1] = last
    #
    # # 转为数组列表
    # level_order = [int(x) for x in level_order if x != 'None']
    level_order = eval(input())

    root = build_tree(level_order)
    print(count_balanced_subtrees(root))


if __name__ == '__main__':
    main()