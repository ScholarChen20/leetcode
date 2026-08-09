from typing import List


def generate(numRows: int) -> List[List[int]]:
    """
    Given an integer numRows, return the first numRows of Pascal's triangle.
    In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:
    generate(numRows = 5) == [[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]
    generate(numRows = 1) == [[1]]
    Constraints:
    1 <= numRows <= 30
    """
    res=[]
    for i in range(numRows):
        res.append([])
        for j in range(i+1):
            if j==0 or j==i:
                res[i].append(1)
            else:
                res[i].append(res[i-1][j-1] + res[i-1][j])
    return  res


if __name__ == '__main__':
    print(generate(5))