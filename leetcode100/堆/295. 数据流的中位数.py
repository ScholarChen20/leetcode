"""
中位数是有序整数列表中的中间值。如果列表的大小是偶数，则没有中间值，中位数是两个中间值的平均值。
例如 arr = [2,3,4] 的中位数是 3 。
例如 arr = [2,3] 的中位数是 (2 + 3) / 2 = 2.5 。
实现 MedianFinder 类:
MedianFinder() 初始化 MedianFinder 对象。
void addNum(int num) 将数据流中的整数 num 添加到数据结构中。
double findMedian() 返回到目前为止所有元素的中位数。与实际答案相差 10-5 以内的答案将被接受。

示例 1：

输入
["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
[[], [1], [2], [], [3], []]
输出
[null, null, null, 1.5, null, 2.0]
"""
import heapq
class MedianFinder:
    """
    可以将数据分为左右两边，一边以最大堆的形式实现，可以快速获得左侧最大数，
另一边则以最小堆的形式实现。其中需要注意的一点就是左右侧数据的长度差不能超过1。
这种实现方式的效率与AVL平衡二叉搜索树的效率相近，但编写更快
    """
    def __init__(self):
        self.min_list = list()
        self.max_list = list()

    def addNum(self, num: int) -> None:
        if not self.min_list or num > self.min_list[0]:
            heapq.heappush(self.min_list, num)
            if len(self.min_list) - len(self.max_list) > 1:
                heapq.heappush(self.max_list, -heapq.heappop(self.min_list))
        else:
            heapq.heappush(self.max_list, -num)
            if len(self.max_list) - len(self.min_list) > 1:
                heapq.heappush(self.min_list, -heapq.heappop(self.max_list))


    def findMedian(self) -> float:
        if len(self.min_list) > len(self.max_list):
            return self.min_list[0]
        return (self.min_list[0] - self.max_list[0]) / 2

if __name__ == '__main__':
    obj = MedianFinder()
    obj.addNum(1)
    obj.addNum(2)
    print(obj.findMedian())
    obj.addNum(3)
    obj.addNum(4)
    print(obj.findMedian())