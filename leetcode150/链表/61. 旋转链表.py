"""
给你一个链表的头节点 head ，旋转链表，将链表每个节点向右移动 k 个位置。

示例 1：
输入：head = [1,2,3,4,5], k = 2
输出：[4,5,1,2,3]

示例 2：
输入：head = [0,1,2], k = 4
输出：[2,0,1]
"""
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def rotateRight(self, head: ListNode, k: int) -> ListNode:
        if not head or not head.next:
            return head

        # 1.计算链表长度
        length = 1
        tail = head
        while tail.next:
            length += 1
            tail = tail.next

        # 2.计算旋转次数
        k = k % length
        if k == 0:
            return head

        # 3. 找倒数k+1个节点 作为新链表的头节点
        new_tail = head
        for _ in range(length - k - 1):
            new_tail = new_tail.next

        # 4. 更新链表
        new_head = new_tail.next
        new_tail.next = None
        tail.next = head

        return new_head

if __name__ == '__main__':
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    head.next.next.next.next = ListNode(5)
    solution = Solution()
    result = solution.rotateRight(head, 2)
    print(result)
