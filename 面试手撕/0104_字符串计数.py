"""
给定一个一亿长度无序字符串（包含26个字母），cpu每秒可以处理1000个字符， 请设计一个算法， 在1000s内完成排序
输入：字符串
输出：排序后字符串

示例：
输入：s = "eat"
输出："aet"
"""
class Solution:
    def sortString(self, s: str) -> str:
        """计数排序，时间复杂度O(n)，空间复杂度O(n)"""
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1
        res = []
        for i in range(26):
            res.extend([chr(i + ord('a'))] * count[i])
        return "".join(res)

if __name__ == '__main__':
    s = Solution()
    print(s.sortString("eat"))
