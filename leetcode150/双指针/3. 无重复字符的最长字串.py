"""
给定一个字符串 s ，请你找出其中不含有重复字符的 最长 子串 的长度。
示例 1:

输入: s = "abcabcbb"
输出: 3
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。注意 "bca" 和 "cab" 也是正确答案。
示例 2:

输入: s = "bbbbb"
输出: 1
解释: 因为无重复字符的最长子串是 "b"，所以其长度为 1。
"""
class Solution:
    def lengthOfLongestSubstring(self, s: str): # 滑动窗口： 借助哈希表判断num是否在set中，如果在set中，则将左指针向右移动，直到num不在set中，然后将num加入set中，然后更新最大长度
        left = 0
        num_set = set()
        max_length = 0
        for str in s:
            if str not in num_set:
                num_set.add(str)
                max_length = max(max_length, len(num_set))
            else:
                while str in num_set:
                    num_set.remove(s[left])
                    left += 1
                num_set.add(str)
        return max_length

if __name__ == '__main__':
    s = Solution()
    str1 = "abcabcbb"
    str2 = "bbbbb"
    print(s.lengthOfLongestSubstring(str1))
    print(s.lengthOfLongestSubstring(str2))