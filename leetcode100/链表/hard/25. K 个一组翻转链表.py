"""
给你链表的头节点 head ，每 k 个节点一组进行翻转，请你返回修改后的链表。
k 是一个正整数，它的值小于或等于链表的长度。如果节点总数不是 k 的整数倍，那么请将最后剩余的节点保持原有顺序。
你不能只是单纯的改变节点内部的值，而是需要实际进行节点交换。
示例 1：

输入：head = [1,2,3,4,5], k = 2
输出：[2,1,4,3,5]
"""
from typing import Optional
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        length = 0
        t = head
        while t:
            t = t.next
            length += 1
            if length == k:break
        if length < k:
            return head

        prev, cur = self.reverseKGroup(t, k), head
        for _ in range(k):
            temp = cur.next
            cur.next = prev
            prev = cur
            cur = temp
        return prev

if __name__ == '__main__':
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    head.next.next.next.next = ListNode(5)
    k = 2
    new_head = Solution().reverseKGroup(head, k)
    list1 = []
    while new_head:
        list1.append(new_head.val)
        new_head = new_head.next
    print(list1)