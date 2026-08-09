import sys
"""
Jack
3
Jack,Tom,Anny,Lucy
Tom,Danny
Jack,Lily

6
"""

from collections import deque

def main():
    """
    Jack
    3
    Jack,Tom,Anny,Lucy
    Tom,Danny
    Jack,Lily
    :return:
    """
    sender = input().strip()

    m = int(input())
    groups = {}
    for _ in range(m):
        parts = input().strip().split()
        group_name = parts[0]
        members = parts[1:]
        groups[group_name] = members

    person_groups = {}
    for group_name, members in groups.items():
        for member in members:
            if member not in person_groups:
                person_groups[member] = []

            person_groups[member].append(group_name)

    visited = set()
    queue = deque()
    visited.add(sender)
    queue.append(sender)

    while queue:
        current = queue.popleft()
        if current not in person_groups:
            continue
        for group in person_groups[current]:
            for member in groups[group]:
                if member not in visited:
                    visited.add(member)
                    queue.append(member)

    print(len(queue))

"""
Jack
3
Jack,Tom,Anny,Lucy
Tom,Danny
Jack,Lily
"""
if __name__ == '__main__':
    main()
