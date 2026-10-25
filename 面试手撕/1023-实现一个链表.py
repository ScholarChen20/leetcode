"""
package com.itheima;

public class Main {
    public static void main(String[] args) {
        MyLinkedList obj = new MyLinkedList();
        int param_1 = obj.get(1);
        System.out.println(param_1);
        obj.addAtHead(2);
        obj.addAtTail(3);
        obj.addAtIndex(1,2);
        obj.deleteAtIndex(2);
    }

    // 实现一个链表. 按下面类实现相关方法.
    // 在线编辑地址: https://www.bejson.com/runcode/java/

    /**
     * Your MyLinkedList object will be instantiated and called as such:
     * MyLinkedList obj = new MyLinkedList();
     * int param_1 = obj.get(index);
     * obj.addAtHead(val);
     * obj.addAtTail(val);
     * obj.addAtIndex(index,val);
     * obj.deleteAtIndex(index);
     */
    static class ListNode{
        public int val;
        public ListNode next;
        public ListNode(int val) {
            this.val = val;
            this.next = null;

        }
    }
    static class MyLinkedList {
        public ListNode head;

        public MyLinkedList() {
            this.head = null;

        }

        public int get(int index) {
            ListNode cur = head;
            int count = 0;
            while(cur != null){
                if(count == index){
                    return cur.val;
                }
                count++;
                cur = cur.next;
            }
            return -1;
        }

        public void addAtHead(int val) {
            ListNode newNode = new ListNode(val);
            newNode.next = head;
            head = newNode;
        }

        public void addAtTail(int val) {
            ListNode newNode = new ListNode(val);
            if(head == null){
                head = newNode;
                return;
            }
            ListNode current = head;
            while(current.next != null){
                current = current.next;
            }
            current.next = newNode;
        }

        public void addAtIndex(int index, int val) {
            if(index == 0){
                addAtHead(val);
                return;
            }
            ListNode current = head;
            int count = 0;
            while(current != null && count < index - 1){
                count++;
                current = current.next;
            }

            ListNode newNode = new ListNode(val);
            newNode.next = current.next;
            current.next = newNode;
        }

        public void deleteAtIndex(int index) {
            if(head == null) return;

            if(index == 0){
                head = head.next;
                return;
            }

            ListNode cur = head;
            int count = 0;
            while(cur != null && count < index - 1){
                count++;
                cur = cur.next;
            }
            cur.next = cur.next.next;
        }
    }

}
"""
