"""
Trie（发音类似 "try"）或者说 前缀树 是一种树形数据结构，用于高效地存储和检索字符串数据集中的键。这一数据结构有相当多的应用情景，例如自动补全和拼写检查。
请你实现 Trie 类：
Trie() 初始化前缀树对象。
void insert(String word) 向前缀树中插入字符串 word 。
boolean search(String word) 如果字符串 word 在前缀树中，返回 true（即，在检索之前已经插入）；否则，返回 false 。
boolean startsWith(String prefix) 如果之前已经插入的字符串 word 的前缀之一为 prefix ，返回 true ；否则，返回 false 。

示例：

输入
["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]
输出
[null, null, true, false, true, null, true]
"""
class Solution:
    """思路： 字典树，每个节点有26个子节点，每个节点表示一个字母，每个节点都有一个标志位，表示是否为单词的结尾"""
    def __init__(self):
        self.children = [None] * 26
        self.isEnd = False

    def insert(self, word: str) -> None:
        node = self # 从根节点开始
        for ch in word:
            index = ord(ch) - ord('a')
            if not node.children[index]:
                node.children[index] = Solution() # 创建新节点
            node = node.children[index]
        node.isEnd = True

    def search(self, word: str) -> bool:
        node = self
        for ch in word:
            index = ord(ch) - ord('a')
            if not node.children[index]:
                return False
            node = node.children[index]
        return node.isEnd

    def startsWith(self, prefix: str) -> bool:
        node = self
        for ch in prefix:
            index = ord(ch) - ord('a')
            if not node.children[index]:
                return False
            node = node.children[index]
        return True

if __name__ == '__main__':
    trie = Solution()
    trie.insert("apple")
    print(trie.search("apple"))
    print(trie.search("app"))
    print(trie.startsWith("app"))
    trie.insert("app")
    print(trie.search("app"))
