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
    def lengthOfLongestSubstring(self, s: str) -> int:
        """滑动窗口, 时间复杂度O(n), 空间复杂度O(n)
        思路： 使用一个set来记录当前窗口中的字符，如果当前字符不在set中，则将当前字符加入set中，否则将窗口左边界向右移动，直到当前字符不在set中，然后将当前字符加入set中，然后更新最大长度"""
        char_set = set()
        left = 0
        max_length = 0
        for str in s:
            if str not in char_set:
                char_set.add(str)
                max_length = max(max_length, len(char_set))
            else:
                while str in char_set: # 移除重复字符
                    char_set.remove(s[left])
                    left += 1
                char_set.add(str) # 添加当前字符
        return max_length

    def lengthOfLongestSubstring2(self, s: str) -> int:
        """暴力枚举，以每个位置作为子串左边界，时间复杂度 O(n^2)，空间复杂度 O(n)。"""
        max_length = 0

        for left in range(len(s)):
            char_set = set()
            for right in range(left, len(s)):
                if s[right] in char_set:
                    break
                char_set.add(s[right])
                max_length = max(max_length, right - left + 1)

        return max_length



if __name__ == '__main__':
    s = Solution()
    str1 = "abcabcbb"
    str2 = "bbbbb"
    print(s.lengthOfLongestSubstring2(str1))
    print(s.lengthOfLongestSubstring2(str2))
