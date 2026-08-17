"""
括号匹配

"""
def isValid(self, s: str) -> bool:
    if len(s) == 1:
        return False
    queue = []
    queue.append(s[:1])
    str = s[1:]
    for char in str:
        if char == ')':
            if len(queue) == 0:  return False
            ch = queue.pop()
            if ch != '(':
                return False
        elif char == ']':
            if len(queue) == 0:  return False
            ch = queue.pop()
            if ch != '[':
                return False
        elif char == '}':
            if len(queue) == 0:  return False
            ch = queue.pop()
            if ch != '{':
                return False
        else:
            queue.append(char)
    if len(queue) != 0:
        return False
    return True


if __name__ == '__main__':
    print(isValid("()))"))