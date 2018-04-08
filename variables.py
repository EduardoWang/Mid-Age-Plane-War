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
        return [self._positionx, self._positiony, self._positionz]

    def getVertexNum(self):
        return self._vertexnum

    def WhichCountry(self):
        return self._country

    def iflighthouse(self):
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


class kindsOfSoldiers(Enum):
    ARCHER = 0
    INFANTRY = 1
    CAVALARY = 2
    LANCER = 3


class counter(Enum):
    INFANTRY = kindsOfSoldiers.LANCER
    LANCER = kindsOfSoldiers.CAVALARY
    CAVALARY = kindsOfSoldiers.INFANTRY


class soldiers:
    def __init__(self, numbers, whichkind, counterSoldier):
        self.num = numbers  # numbers of soldiers
        self.kind = whichkind   # what knid of soldier
        self.counter = counterSoldier



class tech:
    def __init__(self, popu, Attack, movespeed):
        self.population = popu
        self.soldierAttack = Attack  # a dictionary contain soldiers arrack
        self.moveSpeed = movespeed  # similar as above


class playerData:
    def __init__(self, tech, cash, updateneed):
        self.money = cash
        self.upgradeNeed = updateneed
        self.technology = tech
