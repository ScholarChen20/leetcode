"""
给你单链表的头指针 head 和两个整数 left 和 right ，其中 left <= right 。请你反转从位置 left 到位置 right 的链表节点，返回 反转后的链表 。

示例 1：


输入：head = [1,2,3,4,5], left = 2, right = 4
输出：[1,4,3,2,5]
示例 2：

输入：head = [5], left = 1, right = 1
输出：[5]
"""
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def reverseBetween(self, head: ListNode, left: int, right: int) -> ListNode: # 迭代法: 1.找到left节点的前一个节点pre_left和right节点pre_right; 2.反转left到right之间的节点; 3.将pre_left.next指向pre; 4.将pre_right.next指向cur; 5.返回head
        if not head or not head.next:
            return head
        pre = None
        cur = head
        while left > 1:
            pre = cur
            cur = cur.next
            left -= 1
            right -= 1
        pre_left = pre
        pre_right = cur
        while right > 0:
            next = cur.next
            cur.next = pre
            pre = cur
            cur = next
            right -= 1
        if pre_left:
            pre_left.next = pre
        else:
            head = pre
        pre_right.next = cur
        return head

    def reverseBetween2(self, head: ListNode, left: int, right: int) -> ListNode: # 递归法：
        if not head or not head.next:
            return head
        if left == 1:
            return self.reverseN(head, right)
        head.next = self.reverseBetween2(head.next, left - 1, right - 1)
        return head

    def reverseN(self, head: ListNode, n: int) -> ListNode:
        if n == 1:
            return head
        last = self.reverseN(head.next, n - 1)
        next = head.next
        head.next = next.next
        next.next = head
        return last

if __name__ == '__main__':
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    head.next.next.next.next = ListNode(5)
    new_head = Solution().reverseBetween(head, 2, 4)
    while(new_head):
        print(new_head.val, end=" -> ")
        new_head = new_head.next
    print("None")
    new_head = Solution().reverseBetween2(head, 2, 4)
