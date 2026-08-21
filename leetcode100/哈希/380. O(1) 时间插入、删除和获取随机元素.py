"""
实现RandomizedSet 类：

RandomizedSet() 初始化 RandomizedSet 对象
bool insert(int val) 当元素 val 不存在时，向集合中插入该项，并返回 true ；否则，返回 false 。
bool remove(int val) 当元素 val 存在时，从集合中移除该项，并返回 true ；否则，返回 false 。
int getRandom() 随机返回现有集合中的一项（测试用例保证调用此方法时集合中至少存在一个元素）。每个元素应该有 相同的概率 被返回。
你必须实现类的所有函数，并满足每个函数的 平均 时间复杂度为 O(1) 。

示例：

输入
["RandomizedSet", "insert", "remove", "insert", "getRandom", "remove", "insert", "getRandom"]
[[], [1], [2], [2], [], [1], [2], []]
输出
[null, true, false, true, 2, true, false, 2]

"""
from random import choice
class RandomizedSet:

    def __init__(self):
        self.nums=[] # 记录val
        self.indices={} # 记录val的索引

    def insert(self, val: int) -> bool:
        if val in self.indices:
            return False
        self.nums.append(val)
        self.indices[val]=len(self.nums)-1 # 记录val的索引
        return True

    def remove(self, val: int) -> bool:
        if val not in self.indices:
            return False
        index=self.indices[val] # 获取val的索引
        last_val=self.nums[-1]      # 获取最后一个元素
        self.nums[index]=last_val # 将最后一个元素放到要删除的元素的位置
        self.indices[last_val]=index # 更新最后一个元素的索引
        self.nums.pop() # 删除最后一个元素
        del self.indices[val] # 删除val的索引
        return True

    def getRandom(self) -> int:
        """随机返回现有集合中的一项（测试用例保证调用此方法时集合中至少存在一个元素）。每个元素应该有 相同的概率 被返回。"""
        return choice(self.nums)

if __name__ == '__main__':
    randomizedSet = RandomizedSet()
    print(randomizedSet.insert(1))  # 返回 true ，表示 1 被成功地插入。
    print(randomizedSet.remove(2))  # 返回 false ，表示集合中不存在 2 。
    print(randomizedSet.insert(2))  # 返回 true ，表示 2 被成功地插入。
    print(randomizedSet.getRandom())  # getRandom 应随机返回 1 或 2 。
    print(randomizedSet.remove(1))  # 返回 true ，表示 1 被成功地移除。
    print(randomizedSet.insert(2))  # 返回 false ，表示集合中已存在 2 。
    print(randomizedSet.getRandom())  # 由于 2 是集合中唯一的数字，getRandom 总是返回 2 。