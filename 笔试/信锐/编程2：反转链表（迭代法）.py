"""
给出一个链表的头节点，需要你输出反转后的链表头节点，使用迭代法实现
"""
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reverseList(self, head: ListNode) -> ListNode:
        """迭代法反转链表"""
        prev = None
        curr = head
        while curr:
            next_temp = curr.next  # 保存下一个节点
            curr.next = prev       # 反转当前节点的指针
            prev = curr            # 移动 prev 和 curr 指针
            curr = next_temp
        return prev  # prev 最终会指向新的头节点

if __name__ == '__main__':
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
    new_head = Solution().reverseList(head)
    while(new_head):
        print(new_head.val, end=" -> ")
        new_head = new_head.next
    print("None")