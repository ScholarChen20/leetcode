"""
给你一个字符串 s 。我们要把这个字符串划分为尽可能多的片段，同一字母最多出现在一个片段中。例如，字符串 "ababcc" 能够被分为 ["abab", "cc"]，但类似 ["aba", "bcc"] 或 ["ab", "ab", "cc"] 的划分是非法的。
注意，划分结果需要满足：将所有划分结果按顺序连接，得到的字符串仍然是 s 。
返回一个表示每个字符串片段的长度的列表。
示例 1：
输入：s = "ababcbacadefegdehijhklij"
输出：[9,7,8]
解释：
划分结果为 "ababcbaca"、"defegde"、"hijhklij" 。
每个字母最多出现在一个片段中。
像 "ababcbacadefegde", "hijhklij" 这样的划分是错误的，因为划分的片段数较少。
示例 2：
输入：s = "eccbbbbdec"
输出：[10]
"""
from typing import List
def partitionLabels(s: str) -> List[int]:
    """
    思路： 用一个数组记录每个字母最后一次出现的位置，然后用两个指针start和end记录当前片段的起始位置和结束位置，如果i==end，则说明当前片段已经结束，将end-start+1加入到结果中，然后将start更新为i+1
    时间复杂度：O(n)
    空间复杂度：O(1)
    """
    # 定义一个数组
    ans={}
    for i in range(len(s)):
        ans[s[i]] = i

    res = []
    start ,end = 0,0
    for i in range(len(s)):
        j = s[i]
        end = max(end, ans[j] )
        if i == end:
            res.append(end-start+1)
            start = i+1
    return res


if __name__ == '__main__':
    print(partitionLabels("ababcbacadefegdehijhklij"))