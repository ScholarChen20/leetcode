"""
给定一个已排序的链表的头 head ， 删除原始链表中所有重复数字的节点，只留下不同的数字。返回 已排序的链表 。

示例 1：
输入：head = [1,2,3,3,4,4,5]
输出：[1,2,5]

"""
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return head
        prehead = ListNode(0, head) # prehead是头节点的前一个节点
        pre = prehead # pre是当前节点的前一个节点
        cur = head # cur是当前节点

        while cur and cur.next:
            if cur.val == cur.next.val: # 如果当前节点和下一个节点的值相等，则删除当前节点和下一个节点
                while cur and cur.next and cur.val == cur.next.val: # 删除所有重复节点
                    cur = cur.next
                pre.next = cur.next # 删除重复节点
                cur = cur.next # 更新cur
            else:
                pre = cur
                cur = cur.next
        return prehead.next

if __name__ == '__main__':
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(3)
    head.next.next.next.next = ListNode(4)
    head.next.next.next.next.next = ListNode(4)
    head.next.next.next.next.next.next = ListNode(5)

    solution = Solution()
    result = solution.deleteDuplicates(head)

