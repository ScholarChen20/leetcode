"""
请你设计并实现一个满足  LRU (最近最少使用) 缓存 约束的数据结构。
实现 LRUCache 类：
LRUCache(int capacity) 以 正整数 作为容量 capacity 初始化 LRU 缓存
int get(int key) 如果关键字 key 存在于缓存中，则返回关键字的值，否则返回 -1 。
void put(int key, int value) 如果关键字 key 已经存在，则变更其数据值 value ；如果不存在，则向缓存中插入该组 key-value 。如果插入操作导致关键字数量超过 capacity ，则应该 逐出 最久未使用的关键字。
函数 get 和 put 必须以 O(1) 的平均时间复杂度运行。

输入
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
输出
[null, null, null, 1, null, -1, null, -1, 3, 4]
"""
class DLinkNode:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = dict() # 哈希表用于存储key和节点的映射
        self.head = DLinkNode() # 双向链表的头部是最近使用的节点，尾部是最近未使用的节点
        self.tail = DLinkNode() # 双向链表的头部是最近使用的节点，尾部是最近未使用的节点
        self.head.next = self.tail
        self.tail.prev = self.head
        self.capacity = capacity
        self.size = 0

    def get(self, key: int):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self.moveToHead(node)
        return node.value

    def put(self, key: int, value: int):
        if key not in self.cache:
            node = DLinkNode(key, value)
            self.cache[key] = node
            self.addToHead(node)
            self.size += 1
            if self.size > self.capacity:
                # 如果超出容量，删除双向链表的尾部节点
                removed = self.removeTail()
                self.cache.pop(removed.key)
                self.size -= 1
        else:
            # 如果key已存在，更新值并移动到头部
            node = self.cache[key]
            node.value = value
            self.moveToHead(node)

    def moveToHead(self, node: DLinkNode):
        self.removeNode(node) # 先删除节点
        self.addToHead(node) # 再添加到头部

    def removeNode(self, node: DLinkNode):
        node.prev.next= node.next
        node.next.prev = node.prev

    def addToHead(self, node: DLinkNode):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def removeTail(self):
        node = self.tail.prev
        self.removeNode(node)
