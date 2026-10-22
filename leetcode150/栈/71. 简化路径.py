"""
给你一个字符串 path ，表示指向某一文件或目录的 Unix 风格 绝对路径 （以 '/' 开头），请你将其转化为 更加简洁的规范路径。
在 Unix 风格的文件系统中规则如下：
一个点 '.' 表示当前目录本身。
此外，两个点 '..' 表示将目录切换到上一级（指向父目录）。
任意多个连续的斜杠（即，'//' 或 '///'）都被视为单个斜杠 '/'。
任何其他格式的点（例如，'...' 或 '....'）均被视为有效的文件/目录名称。
返回的 简化路径 必须遵循下述格式：

始终以斜杠 '/' 开头。
两个目录名之间必须只有一个斜杠 '/' 。
最后一个目录名（如果存在）不能 以 '/' 结尾。
此外，路径仅包含从根目录到目标文件或目录的路径上的目录（即，不含 '.' 或 '..'）。
返回简化后得到的 规范路径 。

示例 1：
输入：path = "/home/"
输出："/home"
解释：应删除尾随斜杠。

示例 2：
输入：path = "/home//foo/"
输出："/home/foo"
解释：多个连续的斜杠被单个斜杠替换。

示例 3：
输入：path = "/home/user/Documents/../Pictures"
输出："/home/user/Pictures"
解释：两个点 ".." 表示上一级目录（父目录）。

示例 4：
输入：path = "/../"
输出："/"
解释：不可能从根目录上升一级目录。

示例 5：
输入：path = "/.../a/../b/c/../d/./"
输出："/.../b/d"
解释："..." 在这个问题中是一个合法的目录名。
"""
class Solution:
    def simplifyPath(self, path: str) -> str:
        stack = []
        for item in path.split('/'):
            if item == '..':
                if stack:
                    stack.pop()
            elif item != '.' and item != '':
                stack.append(item)
        return '/' + '/'.join(stack)

if __name__ == '__main__':
    s = Solution()
    path = "/home//foo/"
    print(s.simplifyPath(path))