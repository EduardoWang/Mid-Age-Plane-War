from enum import Enum


class vertex:
    def __init__(self, num, xp, yp, zp, terr, coun, lightH, mist):
        self._vertexnum = num
        self._positionx = xp
        self._positiony = yp
        self._positionz = zp
        self.territory = terr
        self._country = coun
        self._lighthouse = lightH
        self.ifmist = mist

    def getPosition(self):
        return (self._positionx, self._positiony, self._positionz)

    def getVertexNum(self):
        return self._vertexnum

    def isCountry(self):
        return self._country

    def islighthouse(self):
        return self._lighthouse


class graph:
    def __init__(self, Vertices=set(), Edges=list()):
        # a dictionary mapping a vertex to its list of neighbours
        self.alist = {}  # empty dictionary

        for v in Vertices:
            self.add_vertex(v)
        for e in Edges:
            self.add_edge(e)

    def get_vertices(self):
        return set(self.alist.keys())

    def get_edges(self):
        edges = []
        for v, l in self.alist.items():
            edges += l
        return edges

    def add_vertex(self, v):
        if v not in self.alist:
            self.alist[v] = []

    def add_edge(self, e):
        if not self.is_vertex(e[0]) or not self.is_vertex(e[1]):
            raise ValueError("An endpoint is not in graph")
        self.alist[e[0]].append(e[1])

    def is_vertex(self, v):
        return v in self.alist

    def is_edge(self, e):
        if e[0] not in self.alist:
            return False

        return e[1] in self.alist[e[0]]

    def neighbours(self, v):
        if not self.is_vertex(v):
            raise ValueError("Vertex not in graph")

        return self.alist[v]


kindsOfSoldiers = {'ARCHER': 0,
                   'INFANTRY': 1,
                   'CAVALRY': 2,
                   'PIKEMAN': 3}

counter = {0: 0,
           1: 3,
           2: 1,
           3: 2}


class soldiers:
    def __init__(self, numbers, whichkind, vernumber, moved):
        self._num = numbers  # numbers of soldiers
        self.kind = whichkind   # what knid of soldier
        self.verNum = vernumber
        self.move = moved

    def getnum(self):
        return self._num

    def setnum(self, number):
        self._num = number


class tech:
    def __init__(self, Attack, movespeed, money):
        self.soldierAttack = Attack  # a dictionary contain soldiers arrack
        self.moveSpeed = movespeed  # similar as above
        self.moneyperTurn = money


class playerData:
    def __init__(self, cash, technology=0, updateneed=0):
        self.money = cash
        self.upgradeNeed = updateneed
        self.tech = technology
