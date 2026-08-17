"""
给你一个链表，两两交换其中相邻的节点，并返回交换后链表的头节点。你必须在不修改节点内部的值的情况下完成本题（即，只能进行节点交换）。
示例 1：


输入：head = [1,2,3,4]
输出：[2,1,4,3]
"""
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def swapPairs(self, head: ListNode):
        prehead = ListNode(0, head)
        pre = prehead
        cur = head
        while cur and cur.next:
            next = cur.next
            cur.next = next.next
            next.next = cur
            pre.next = next
            pre = cur
            cur = cur.next
        return prehead.next

if __name__ == '__main__':
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    cur = Solution().swapPairs(head)
    list1 = []
    while cur:
        list1.append(cur.val)
        cur = cur.next
    print(list1)