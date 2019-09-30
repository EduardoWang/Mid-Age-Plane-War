from collections import deque
from variables import graph
from variables import vertex


def breadth_first_search(searchG, s, d):
    R = dict()
    R[s] = s
    Q = deque()
    Q.append(s)
    while Q:
        u = Q.popleft()
        for v in searchG.neighbours(u):
            if v not in R:
                R[v] = u
                Q.append(v)
    ptNow = d
    result = [d]
    if d not in R.keys():
        return []
    while ptNow != s:
        ptNow = R[ptNow]
        result.append(ptNow)
    result.reverse()
    return result


def loadmap(filename):
    inputFile = open(filename, "r")
    lines = inputFile.readlines()
    vertexData = dict()
    g = graph()
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip().split(",")
    for l in lines:
        if l[0] == "V":
            temp = vertex(int(l[1]), int(l[2]), int(l[3]), int(l[4]),
                          l[5], bool(int(l[6])), bool(int(l[7])), True)
            g.add_vertex(int(l[1]))
            vertexData[int(l[1])] = temp
        elif l[0] == "E":
            g.add_edge((int(l[1]), int(l[2])))
            g.add_edge((int(l[2]), int(l[1])))
    return g, vertexData


def findenemy(soldierData, RvertexData):
    result = dict()
    for i in RvertexData.keys():
        if RvertexData[i].ifmist is False and \
                soldierData[i].getnum() != 0:
            result[i] = soldierData[i]
    if result is None:
        return False
    return result
