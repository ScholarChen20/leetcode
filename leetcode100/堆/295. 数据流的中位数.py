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
    找中位数本质就是找有序序列中间位置的值。如果每次都排序再取中间值，插入一次是 (O(n \log n))。用两个堆可以把数据"劈成两半"：
    大根堆（存较小的一半，堆顶是这半边的最大值） heapq 只实现了小根堆（堆顶永远是最小值），没有现成的大根堆。要模拟大根堆，标准技巧就是取相反数：原值 5, 3, 8 存进去变成 -5, -3, -8
    小根堆（存较大的一半，堆顶是这半边的最小值）
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
        if len(self.min_list) < len(self.max_list):
            return -self.max_list[0]
        return (self.min_list[0] - self.max_list[0]) / 2

if __name__ == '__main__':
    obj = MedianFinder()
    obj.addNum(1)
    obj.addNum(2)
    print(obj.findMedian())
    obj.addNum(3)
    obj.addNum(4)
    print(obj.findMedian())