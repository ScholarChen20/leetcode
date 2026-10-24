"""
给你一个链表数组，每个链表都已经按升序排列。
请你将所有链表合并到一个升序链表中，返回合并后的链表。
示例 1：

输入：lists = [[1,4,5],[1,3,4],[2,6]]
输出：[1,1,2,3,4,4,5,6]
解释：链表数组如下：
[
  1->4->5,
  1->3->4,
  2->6
]
将它们合并到一个有序链表中得到。1->1->2->3->4->4->5->6

示例 2：
输入：lists = []
输出：[]

示例 3：
输入：lists = [[]]
输出：[]
"""
from typing import List
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeKLists(self, lists: List[ListNode]) -> ListNode:
        if not lists: return
        n = len(lists)
        return self.merge(lists, 0, n - 1)

    def merge(self, lists, left, right):
        if left == right:
            return lists[left]
        mid = (left + right) // 2
        l1 = self.merge(lists, left, mid)
        l2 = self.merge(lists, mid + 1, right)
        return self.mergeTwoList(l1, l2)

    def mergeTwoList(self, l1: List[ListNode], l2: List[ListNode]): # 递归法
        if not l1: return l2
        if not l2: return l1
        if l1.val < l2.val:
            l1.next = self.mergeTwoList(l1.next, l2)
            return l1
        else:
            l2.next = self.mergeKLists(l1, l2.next)
            return l2

    def mergeTwoList2(self, l1: List[ListNode], l2: List[ListNode]): # 迭代法
        cur = dummy = ListNode()
        while l1 and l2:
            if l1.val < l2.val:
                cur.next = l1
                l1 = l1.next
            else:
                cur.next = l2
                l2 = l2.next
            cur = cur.next
        cur.next = l1 if l1 else l2
        return dummy.next

if __name__ == '__main__':
    print(Solution().mergeKLists([[1,4,5],[1,3,4],[2,6]]))