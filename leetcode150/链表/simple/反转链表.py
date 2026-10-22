"""
https://leetcode.cn/problems/reverse-linked-list/
给你单链表的头节点 head ，请你反转链表，并返回反转后的链表。

示例 1：
输入：head = [1,2,3,4,5]
输出：[5,4,3,2,1]
示例 2：
输入：head = [1,2]
输出：[2,1]
示例 3：
输入：head = []
输出：[]
"""

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reverseList(self, head: ListNode):
        if not head or not head.next:
            return head

        pre = None
        cur = head
        while cur:
            next_temp = cur.next
            cur.next = pre
            pre = cur
            cur = next_temp
        return pre

if __name__ == '__main__':
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
    new_head = Solution().reverseList(head)