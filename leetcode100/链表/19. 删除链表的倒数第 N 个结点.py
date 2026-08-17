"""
给你一个链表，删除链表的倒数第 n 个结点，并且返回链表的头结点。
示例 1：


输入：head = [1,2,3,4,5], n = 2
输出：[1,2,3,5]
"""
from typing import Optional
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def removeNthFromEnd(self, head: ListNode, n: int) -> ListNode:
        prehead = ListNode(0, head)
        slow = head
        fast = prehead
        for i in range(n):
            slow = slow.next

        while slow:
            slow = slow.next
            fast = fast.next

        fast.next = fast.next.next
        return prehead.next

if __name__ == '__main__':
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    head.next.next.next.next = ListNode(5)
    cur = Solution().removeNthFromEnd(head, 2)
    list1 = []
    while cur:
        list1.append(cur.val)
        cur = cur.next
    print(list1)
