"""
走楼梯，一部只能走一格或者两格，求到顶楼有多少种走法
"""
def climbStairs(n: int) -> int:
    dp = [0] * (n+1)
    dp[0]=1
    dp[1]=2
    if n == 1 or n == 2:
        return dp[n-1]
    for i in range(2, n):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n-1]


if __name__ == '__main__':
    print(climbStairs(44))