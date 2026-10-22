"""
给定两个非空链表来表示两个非负整数。位数按照逆序方式存储，它们的每个节点只存储单个数字。将两数相加返回一个新的链表。

你可以假设除了数字 0 之外，这两个数字都不会以零开头。

示例：

输入：(2 -> 4 -> 3) + (5 -> 6 -> 4)
输出：7 -> 0 -> 8
原因：342 + 465 = 807
"""
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None
from typing import List
class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        """
        模拟法，从头到尾遍历两个链表，每次相加，如果大于10，则进位，否则不进位
        """
        if not l1:
            return l2
        if not l2:
            return l1
        dummy = ListNode(0) # 创建一个虚拟头节点，用于返回结果链表
        cur = dummy # 创建一个指针，用于遍历结果链表
        carry = 0
        while l1 or l2:
            if l1:
                carry += l1.val
                l1 = l1.next
            if l2:
                carry += l2.val
                l2 = l2.next
            cur.next = ListNode(carry % 10) # 创建一个节点，用于存储相加的结果
            cur = cur.next
            carry //= 10

        if carry:
            cur.next = ListNode(carry) # 如果最后还有进位，需要创建一个节点，用于存储进位
        return dummy.next

if __name__ == '__main__':
    l1 = ListNode(2)
    l1.next = ListNode(4)
    l1.next.next = ListNode(3)
    l2 = ListNode(5)
    l2.next = ListNode(6)
    l2.next.next = ListNode(4)
    print(Solution().addTwoNumbers(l1, l2))