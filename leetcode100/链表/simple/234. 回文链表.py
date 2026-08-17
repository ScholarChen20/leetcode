"""
给你一个单链表的头节点 head ，请你判断该链表是否为回文链表。如果是，返回 true ；否则，返回 false 。
示例 1：

输入：head = [1,2,2,1]
输出：true
"""
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        '解法一：转数组'
        arr = []
        while head is not None:
            arr.append(head.val)
            head = head.next
        return arr == arr[::-1]

class Solution1:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        '解法二：快慢指针+反转链表'
        if not head or not head.next:
            return True

        # 找到链表的中点
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        # 反转后半部分链表
        prev = None
        while slow:
            next_node = slow.next
            slow.next = prev
            prev = slow
            slow = next_node

        # 比较前半部分和后半部分
        left, right = head, prev
        while right:  # 只需要比较后半部分的长度
            if left.val != right.val:
                return False
            left = left.next
            right = right.next

        return True

if __name__ == '__main__':
    # 构建链表 1 -> 2 -> 2 -> 1
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(2)
    head.next.next.next = ListNode(1)

    # print(Solution().isPalindrome(head))  # 输出: True
    print(Solution1().isPalindrome(head))  # 输出: True