import pygame
import sys
import Functions
import math
import copy
import random

from variables import soldiers
from variables import kindsOfSoldiers
from variables import counter
from variables import playerData
from variables import tech
from Functions import breadth_first_search
from Functions import findenemy

# initial all global variable needed
mapgraph, vertexData = Functions.loadmap("map1.txt")
LvertexData = copy.deepcopy(vertexData)
RvertexData = copy.deepcopy(vertexData)
positionData = dict()

initialTech = tech(1, 2, 500)
updateneed = {'attack': 100, 'speed': 300, 'money': 500}

Player = playerData(500, initialTech, updateneed)
Com = playerData(500, initialTech, updateneed)
playerSoldier = dict()
ComSoldier = dict()
for ver in mapgraph.get_vertices():
    playerSoldier[ver] = soldiers(0, None, -1, False)
    ComSoldier[ver] = soldiers(0, None, -1, False)


# Computer AI's army if they are the same kind by adding up the num and erase
# the one in the start address
def combine(s, d):
    num = ComSoldier[d].getnum() + ComSoldier[s].getnum()
    ComSoldier[d].setnum(num)
    ComSoldier[d].move = True
    ComSoldier[s] = soldiers(0, None, -1, False)


# move AI's army if no army in the destination
def justmove(s, d):
    # copy the status to soldier at the destination and change move to True
    # Erase the one at start address.
    num = ComSoldier[s].getnum()
    ComSoldier[d].setnum(num)
    ComSoldier[d].kind = ComSoldier[s].kind
    ComSoldier[d].verNum = d
    ComSoldier[d].move = True
    ComSoldier[s] = soldiers(0, None, -1, False)


# move AI's army
def movesoldier(path):
    # take the part of the path equals to the maximum amount to move
    if len(path) > Com.tech.moveSpeed:
        path = path[0:Com.tech.moveSpeed+1]
    for point in range(1, len(path)):
        # if there is AI's soldier in the destination, check if they are the
        # same kind as the soldier at the start address. If so, combine, else,
        # no process
        if ComSoldier[path[point]].getnum() != 0:
            kind1 = ComSoldier[path[point]].kind
            kind2 = ComSoldier[path[point-1]].kind
            if kind1 != kind2:
                return
            else:
                combine(point, path[point-1])
        # if there is no AI's soldier at the start address, no process required
        elif ComSoldier[path[point-1]].getnum() == 0:
            return
        # if there is player's soldier in the destination, call com_battle
        elif playerSoldier[path[point]].getnum() != 0:
            com_battle(path[point-1], path[point])
        # if no soldier in the destination, just move
        else:
            justmove(path[point-1], path[point])
        # add a delay to AI for player to better observe AI's operation
        pygame.time.wait(100)
        # redraw the map with the all the changes
        refresh()
        pygame.display.flip()
    # change all the move status of the moved soldiers to be True
    ComSoldier[path[point]].move = True


# calculate the result when AI's army attack player's
def com_battle(s, d):
    # get the kind and num for soldier of both side and calculate the left
    # amount by subtract AI's amount by player's amount
    player_kind = playerSoldier[d].kind
    com_kind = ComSoldier[s].kind

    num_p = playerSoldier[d].getnum()*Player.tech.soldierAttack
    num_c = ComSoldier[s].getnum()*Com.tech.soldierAttack
    left = num_c - num_p
    # if player's soldier counter AI's soldier, double the player's amount
    if counter[player_kind] == com_kind:
        left -= num_p
        # if left >= 0, AI win the battle, change the AI's amount to be left and
        # erase player's army
        if left >= 0:
            ComSoldier[d].setnum(int(left/Com.tech.soldierAttack))
            ComSoldier[d].kind = ComSoldier[s].kind
            ComSoldier[d].verNum = d
            ComSoldier[s] = soldiers(0, None, -1, False)
            playerSoldier[d] = soldiers(0, None, -1, False)
        # else, player win, change the amount of player soldier to be left and
        # erase the AI's soldier
        else:
            ComSoldier[s] = soldiers(0, None, -1, False)
            playerSoldier[d].setnum(int(-left/Player.tech.soldierAttack))
    # if AI counters player, double the AI's army and proceed with the same
    # calculation
    elif counter[com_kind] == player_kind:
        left += num_c
        if left >= 0:
            ComSoldier[d].setnum(int(left/2/Com.tech.soldierAttack))
            ComSoldier[d].kind = ComSoldier[s].kind
            ComSoldier[d].verNum = d
            ComSoldier[s] = soldiers(0, None, -1, False)
            playerSoldier[d] = soldiers(0, None, -1, False)
        else:
            ComSoldier[s] = soldiers(0, None, -1, False)
            playerSoldier[d].setnum(int(-left/Player.tech.soldierAttack))
    # if no counter relation, directly proceed with the calculation above
    else:
        if left >= 0:
            ComSoldier[d].setnum(int(left/Com.tech.soldierAttack))
            ComSoldier[d].kind = ComSoldier[s].kind
            ComSoldier[d].verNum = d
            ComSoldier[s] = soldiers(0, None, -1, False)
            playerSoldier[d] = soldiers(0, None, -1, False)
        else:
            ComSoldier[s] = soldiers(0, None, -1, False)
            playerSoldier[d].setnum(int(-left/Player.tech.soldierAttack))
    ComSoldier[d].move = True


# operation when no player's army is observed by the AI
def farming():
    # upgrade random technology every 5 rounds until not enough money
    if roundnum % 5 == 0:
        up = random.randint(0, 3)
        if up == 1 and Com.tech.soldierAttack <= 2:
            Com.tech.soldierAttack += 0.25
            Com.money -= Com.upgradeNeed['attack']
            Com.upgradeNeed['attack'] += 100
        elif up == 2 and Com.tech.moveSpeed <= 4:
            Com.tech.moveSpeed += 1
            Com.money -= Com.upgradeNeed['speed']
            Com.upgradeNeed['speed'] += 200
        elif up == 3:
            Com.tech.moneyperTurn += 500
            Com.money -= Com.upgradeNeed['money']

    if Com.money == 0:
        return

    # train different soldier in other rounds or use the left money to train
    # archer
    if roundnum % 5 == 1:
        ComSoldier[45] = soldiers(Com.money, kindsOfSoldiers['INFANTRY'], 45, False)
    elif roundnum % 5 == 2:
        ComSoldier[54] = soldiers(Com.money, kindsOfSoldiers['CAVALRY'], 54, False)
    elif roundnum % 5 == 3:
        ComSoldier[46] = soldiers(Com.money, kindsOfSoldiers['PIKEMAN'], 46, False)
    else:
        ComSoldier[55] = soldiers(Com.money, kindsOfSoldiers['ARCHER'], 55, False)

    # move all soldiers toward the player's base use the breadth_first_search to
    # calculate the shortest path and call the movesoldier
    closest = 100
    for i in ComSoldier.keys():
        if ComSoldier[i].getnum() != 0 and ComSoldier[i].move is False:
            distance = len(breadth_first_search(mapgraph, i, 10))
            base_ver = 10
            if distance > len(breadth_first_search(mapgraph, i, 17)):
                distance = len(breadth_first_search(mapgraph, i, 17))
                base_ver = 17
            if distance > len(breadth_first_search(mapgraph, i, 16)):
                distance = len(breadth_first_search(mapgraph, i, 16))
                base_ver = 16
            if distance < closest:
                att_ver = base_ver

            att_path = breadth_first_search(mapgraph, i, att_ver)
            movesoldier(att_path)


# operation when player's army is observed by the AI
def enemyfound():
    # get the vertex and other information about the enemy which is closest to
    # the AI's base
    enemy = findenemy(playerSoldier, RvertexData)
    closest = 100
    for i in enemy.keys():
        distance = len(breadth_first_search(mapgraph, i, 45))
        base_ver = 45
        if distance > len(breadth_first_search(mapgraph, i, 46)):
            distance = len(breadth_first_search(mapgraph, i, 46))
            base_ver = 46
        if distance > len(breadth_first_search(mapgraph, i, 54)):
            distance = len(breadth_first_search(mapgraph, i, 54))
            base_ver = 54
        if distance < closest:
            closest = distance
            enm_ver = i
            build_ver = base_ver

    # train the counter soldier with all money you own
    enm_kind = playerSoldier[enm_ver].kind
    for k in counter.keys():
        if counter[k] == enm_kind:
            buildkind = k
            break
    if enm_kind != 0:
        ComSoldier[build_ver] = \
            soldiers(Com.money, buildkind, build_ver, False)
    else:
        ComSoldier[build_ver] = \
            soldiers(Com.money, 0, build_ver, False)

    # find the soldier that is closest to the enemy's base as attack soldier
    closest = 100
    for i in ComSoldier.keys():
        if ComSoldier[i].getnum() != 0 and ComSoldier[i].move is False:
            distance = len(breadth_first_search(mapgraph, i, 10))
            base_ver = 10
            if distance > len(breadth_first_search(mapgraph, i, 17)):
                distance = len(breadth_first_search(mapgraph, i, 17))
                base_ver = 17
            if distance > len(breadth_first_search(mapgraph, i, 16)):
                distance = len(breadth_first_search(mapgraph, i, 16))
                base_ver = 16
            if distance < closest:
                closest = distance
                com_ver = i
                att_ver = base_ver

    # move all soldier except the attack soldier to defend the enemy and move
    # move the attack soldier toward player's base
    for key in ComSoldier.keys():
        if ComSoldier[key].getnum() != 0 and ComSoldier[key].move is False:
            if key != com_ver:
                def_path = breadth_first_search(mapgraph, key, enm_ver)
                movesoldier(def_path)

            else:
                att_path = breadth_first_search(mapgraph, com_ver, att_ver)
                movesoldier(att_path)


# Overall AI's operation
def Computer():
    # change all move status of AI's army to False
    for s in ComSoldier.keys():
        if ComSoldier[s].getnum() != 0:
            ComSoldier[s].move = False
    # call enemyfound if player's army is observed, else call farming
    if findenemy(playerSoldier, RvertexData):
        enemyfound()
    else:
        farming()


# Player part
# draw the soldier selected page when in produce mode
def drawPic():
    screen.blit(soldier_back, (0, 0))
    for i in range(len(soldier_select)):
        soldier_select[i] = pygame.transform.scale(soldier_select[i], (70, 90))
    for i in range(len(soldier_select)):
        screen.blit(soldier_select[i], (88, i*85+90))


# start page of the game
def startMode():
    startGraph = pygame.image.load("start.jpg")
    startGraph_rect = startGraph.get_rect()
    description = pygame.image.load("Description.JPG")
    descriText = mytext.render('DESCRIPTION', True, (255, 255, 255))
    draw = False
    while True:
        mouse = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = True
            elif event.type == pygame.KEYDOWN:
                draw = False
        x, y = pygame.mouse.get_pos()

        screen.blit(startGraph, startGraph_rect)
        screen.blit(descriText, (540, 830))

        if abs(x-640) < 140 and abs(y-684) < 65:
            pygame.draw.rect(screen, (255, 255, 0), (500, 619, 280, 135), 5)
        elif abs(x-640) < 140 and abs(y-840) < 40:
            pygame.draw.rect(screen, (255, 255, 0), (500, 800, 280, 80), 5)
        if mouse:
            if abs(x-640) < 140 and abs(y-684) < 65:
                break
            elif abs(x-640) < 140 and abs(y-840) < 40:
                draw = True
        if draw:
            screen.blit(description, (177, 200))
        pygame.display.flip()


# initial set all data needed
def initialData():
    L = dict()
    R = dict()
    for v in vertexData.keys():
        x, y, z = vertexData[v].getPosition()
        positionData[v] = \
            [680 + 83*y*math.cos(math.pi/3) + 83*z*math.cos(math.pi/3),
             590 - x*39 - 39*y*math.sin(math.pi/3) + 39*z*math.sin(math.pi/3)]
        if (vertexData[v].isCountry() or vertexData[v].islighthouse()) \
           and vertexData[v].territory == "L":
            L[v] = vertexData[v]
            LvertexData[v].ifmist = False
        elif (vertexData[v].isCountry() or vertexData[v].islighthouse()) \
                and vertexData[v].territory == "R":
            R[v] = vertexData[v]
            RvertexData[v].ifmist = False

    for ver in vertexData.keys():
        x, y, z = vertexData[ver].getPosition()
        for a in L.keys():
            xNew, yNew, zNew = L[a].getPosition()
            if abs(xNew-x)+abs(yNew-y)+abs(zNew-z) <= 4:
                LvertexData[ver].ifmist = False
                break
        for b in R.keys():
            xNew, yNew, zNew = R[b].getPosition()
            if abs(xNew-x)+abs(yNew-y)+abs(zNew-z) <= 4:
                RvertexData[ver].ifmist = False
                break


# print UI with delay
def initialPrint():
    screen.blit(background, back_rect)
    for i in mapgraph.get_vertices():
        x, y = positionData[i]
        pointlist = [(x, y - 40),
                     (x + 37, y - 40*math.sin(math.pi/6)),
                     (x + 37, y + 40*math.sin(math.pi/6)),
                     (x, y + 40),
                     (x - 37, y + 40*math.sin(math.pi/6)),
                     (x - 37, y - 40*math.sin(math.pi/6))]
        if LvertexData[i].isCountry():
            if LvertexData[i].territory == "L":
                pygame.draw.polygon(screen, (153, 226, 255), pointlist)
            else:
                pygame.draw.polygon(screen, (255, 0, 0), pointlist)
            pygame.time.wait(20)
            pygame.display.flip()
        elif LvertexData[i].ifmist is True:
            pygame.draw.polygon(screen, (0, 0, 0), pointlist)
            pygame.time.wait(20)
            pygame.display.flip()
        else:
            if LvertexData[i].territory == "L":
                pygame.draw.polygon(screen, (235, 255, 174), pointlist)
            else:
                pygame.draw.polygon(screen, (255, 164, 128), pointlist)
            if LvertexData[i].islighthouse():
                x, y = positionData[i]
                screen.blit(lightHouse, (x-40, y-40))
            pygame.time.wait(20)
            pygame.display.flip()


# print a hexgon with x y position, color and edge width
# x y is located at the centre of the hexgon you want to draw
# if width is 0, it is a filled hexgon
def printhexgon(x, y, color, width=0):
    pointlist = [(x, y - 40),
                 (x + 37, y - 40*math.sin(math.pi/6)),
                 (x + 37, y + 40*math.sin(math.pi/6)),
                 (x, y + 40),
                 (x - 37, y + 40*math.sin(math.pi/6)),
                 (x - 37, y - 40*math.sin(math.pi/6))]
    pygame.draw.polygon(screen, color, pointlist, width)


# print soldier based on soldier data
def printSoldier():
    for ps in playerSoldier.keys():
        if playerSoldier[ps].getnum() != 0:
            psVer = playerSoldier[ps].verNum
            skind = playerSoldier[ps].kind
            x, y = positionData[psVer]
            screen.blit(print_soldier[skind], (x-35, y-35))
    for cs in ComSoldier.keys():
        if ComSoldier[cs].getnum() != 0:
            csVer = ComSoldier[cs].verNum
            ckind = ComSoldier[cs].kind
            x, y = positionData[csVer]
            if (LvertexData[csVer].isCountry() and
                LvertexData[csVer].territory == "R") or \
                    LvertexData[csVer].ifmist:
                continue
            else:
                ckind = ComSoldier[cs].kind
                x, y = positionData[csVer]
                screen.blit(print_soldier[ckind], (x-35, y-35))


# return the vertex number of mouse currently on
def getmouseVertex():
    x, y = pygame.mouse.get_pos()
    for v in positionData.keys():
        vx, vy = positionData[v]
        if abs(vx-x) <= 35 and abs(vy-y) <= 35:
            return vx, vy
    return 0, 0


# print UI without delay
def gameprint():
    screen.blit(background, back_rect)
    for i in mapgraph.get_vertices():
        x, y = positionData[i]
        if LvertexData[i].isCountry():
            if LvertexData[i].territory == "L":
                printhexgon(x, y, (153, 226, 255))
            else:
                printhexgon(x, y, (255, 0, 0))
        elif LvertexData[i].ifmist is True:
            printhexgon(x, y, (0, 0, 0))
        else:
            if LvertexData[i].territory == "L":
                printhexgon(x, y, (235, 255, 174))
            else:
                printhexgon(x, y, (255, 164, 128))
            if LvertexData[i].islighthouse():
                x, y = positionData[i]
                screen.blit(lightHouse, (x-40, y-40))


# update terrtory data and mist
def update():
    # update map information for player
    for s1 in playerSoldier.keys():
        if playerSoldier[s1].getnum() != 0:
            TempSoldier1 = playerSoldier[s1]
            for i in LvertexData.keys():
                x, y, z = LvertexData[i].getPosition()
                sx, sy, sz = LvertexData[TempSoldier1.verNum].getPosition()
                if abs(x-sx)+abs(y-sy)+abs(z-sz) <= 2:
                    LvertexData[i].ifmist = False
                LvertexData[TempSoldier1.verNum].territory = "L"
                RvertexData[TempSoldier1.verNum].territory = "L"
    # update map information for computer
    for s2 in ComSoldier.keys():
        if ComSoldier[s2].getnum() != 0:
            TempSoldier2 = ComSoldier[s2]
            for i in RvertexData.keys():
                x, y, z = LvertexData[i].getPosition()
                sx, sy, sz = LvertexData[TempSoldier2.verNum].getPosition()
                if abs(x-sx)+abs(y-sy)+abs(z-sz) <= 2:
                    RvertexData[i].ifmist = False
                LvertexData[TempSoldier2.verNum].territory = "R"
                RvertexData[TempSoldier2.verNum].territory = "R"


# return the number you entered
def get_and_print_message():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                return '0'
            elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                return '1'
            elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                return '2'
            elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                return '3'
            elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                return '4'
            elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                return '5'
            elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                return '6'
            elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                return '7'
            elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                return '8'
            elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                return '9'
            elif event.key == pygame.K_q:
                return 'end'


# calculate the result of a battle when player's soldier meet the AI's soldier
# and show the result
def player_battle(s, d):
    # get the soldier type for each side and calculate the left army's amount
    player_kind = playerSoldier[s].kind
    com_kind = ComSoldier[d].kind
    num_p = playerSoldier[s].getnum()*Player.tech.soldierAttack
    num_c = ComSoldier[d].getnum()*Com.tech.soldierAttack
    left = num_p - num_c
    # check if there is a counter relation
    # if yes, add the effect of the counter to the result
    # if player's army counter the AI's army, double the player's army
    if counter[player_kind] == com_kind:
        left += num_p
        # if left >= 0, player's army win the battle with the amount of left,
        # and the AI's army has amount 0. Destination move status becomes True
        if left >= 0:
            playerSoldier[d].setnum(int(left/2/Player.tech.soldierAttack))
            playerSoldier[d].kind = playerSoldier[s].kind
            playerSoldier[d].verNum = d
            playerSoldier[s] = soldiers(0, None, -1, False)
            ComSoldier[d] = soldiers(0, None, -1, False)
        # else, AI's army win with the left amount and player's army becomes 0
        else:
            playerSoldier[s] = soldiers(0, None, -1, False)
            ComSoldier[d].setnum(int(-left/Com.tech.soldierAttack))
    # if AI's army counters player's army, double AI's army and repeat the
    # calculation above
    elif counter[com_kind] == player_kind:
        left -= num_c
        if left >= 0:
            playerSoldier[d].setnum(int(left/Player.tech.soldierAttack))
            playerSoldier[d].kind = playerSoldier[s].kind
            playerSoldier[d].verNum = d
            playerSoldier[s] = soldiers(0, None, -1, False)
            ComSoldier[d] = soldiers(0, None, -1, False)
        else:
            playerSoldier[s] = soldiers(0, None, -1, False)
            ComSoldier[d].setnum(int(-left/Com.tech.soldierAttack))
    # if no counter relation, directly do the same calculation above
    else:
        if left >= 0:
            playerSoldier[d].setnum(int(left/Player.tech.soldierAttack))
            playerSoldier[d].kind = playerSoldier[s].kind
            playerSoldier[d].verNum = d
            playerSoldier[s] = soldiers(0, None, -1, False)
            ComSoldier[d] = soldiers(0, None, -1, False)
        else:
            playerSoldier[s] = soldiers(0, None, -1, False)
            ComSoldier[d].setnum(int(-left/Com.tech.soldierAttack))
    playerSoldier[d].move = True


# move player's army (attack mode in description)
def player_moveSoldier(s, d):
    # if there is no soldier initialy in the destination, simply move the
    # soldier by changing the corresponded element in the dictionary
    if playerSoldier[d].getnum() == 0 and ComSoldier[d].getnum() == 0:
        num = playerSoldier[s].getnum()
        playerSoldier[d].setnum(num)
        playerSoldier[d].kind = playerSoldier[s].kind
        playerSoldier[d].verNum = d
        playerSoldier[s] = soldiers(0, None, -1, False)
    # if the start address has no player's army, return (no process)
    elif playerSoldier[s].getnum() == 0:
        return 1
    # if there is player's army in the destination, check if they are the same
    # kind. If so, add up, else, no process
    elif playerSoldier[d].getnum() != 0:
        if playerSoldier[d].kind != playerSoldier[s].kind:
            return 1
        else:
            number_s = playerSoldier[s].getnum()
            number_d = playerSoldier[d].getnum()
            playerSoldier[d].setnum(number_s + number_d)
            playerSoldier[s] = soldiers(0, None, -1, False)
    # if there are AI's army in the destination, attack by calling player_battle
    elif ComSoldier[d].getnum() != 0:
        player_battle(s, d)
    # redraw the map with all process and calculation finished
    refresh()
    pygame.display.flip()
    return 0


# attack mode of player
def attack():
    selectedVer = -1
    targetVer = -1
    while True:
        button = False
        for event in pygame.event.get():
            if event == pygame.QUIT:
                sys.exit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    return
        refresh()
        x, y = getmouseVertex()
        # selected a vertex with soldier
        if not x == 0 and not y == 0:
            printhexgon(x, y, (0, 72, 255), 7)
        if button:
            for i in positionData.keys():
                if positionData[i] == [x, y]:
                    selectedVer = i
            if selectedVer == -1:
                continue
            # if vertex no soldier, print error message
            if playerSoldier[selectedVer].getnum() == 0 or \
                    playerSoldier[selectedVer].move is True:
                errorMessage = \
                    mytext.render('Please Select a valid Vertex',
                                  True, (0, 0, 0))
                screen.blit(smallwindow, smallwindow_rect)
                screen.blit(errorMessage, (460, 480))
                pygame.display.flip()
                pygame.time.wait(2000)
            else:
                break
        pygame.display.flip()
    while True:
        # select target vertex you want to move
        button2 = False
        for event in pygame.event.get():
            if event == pygame.QUIT:
                sys.exit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button2 = True
        refresh()
        x2, y2 = getmouseVertex()
        selectedX, selectedY = positionData[selectedVer]
        printhexgon(selectedX, selectedY, (0, 72, 255), 7)

        if not x2 == 0 and not y2 == 0:
            printhexgon(selectedX, selectedY, (0, 72, 255), 7)
            printhexgon(x2, y2, (0, 72, 255), 7)
        if button2:
            for i in positionData.keys():
                if positionData[i] == [x2, y2]:
                    targetVer = i
            if targetVer == -1:
                continue
            path = \
                Functions.breadth_first_search(mapgraph, selectedVer, targetVer)
            if len(path) > Player.tech.moveSpeed:
                path = path[0:Player.tech.moveSpeed+1]
            current = path[0]
            for i in range(1, len(path)):
                if player_moveSoldier(current, path[i]):
                    break
                current = path[i]
                refresh()
                pygame.time.wait(100)
                pygame.display.flip()
            if current == path[-1]:
                playerSoldier[current].move = True
            break
        pygame.display.flip()


# soldier produce mode of player
def produce():
    while True:
        mousePress = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mousePress = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    return
        refresh()
        x, y = pygame.mouse.get_pos()
        # get the soldier player want tp produce
        sver = 0
        if abs(x-123) <= 35:
            if abs(y-135) <= 45:
                pygame.draw.rect(screen, (255, 255, 0), (88, 90, 70, 90), 5)
                sver = 4
                skind = kindsOfSoldiers['ARCHER']
            elif abs(y-220) <= 45:
                pygame.draw.rect(screen, (255, 255, 0), (88, 175, 70, 90), 5)
                sver = 10
                skind = kindsOfSoldiers['INFANTRY']
            elif abs(y-305) <= 45:
                pygame.draw.rect(screen, (255, 255, 0), (88, 260, 70, 90), 5)
                sver = 16
                skind = kindsOfSoldiers['CAVALRY']
            elif abs(y-390) <= 45:
                pygame.draw.rect(screen, (255, 255, 0), (88, 345, 70, 90), 5)
                sver = 17
                skind = kindsOfSoldiers['PIKEMAN']
        # get the number player want to produce and produce it
        if mousePress and sver != 0:
            screen.blit(smallwindow, smallwindow_rect)
            message = mytext.render("Please enter a value: ", True, (0, 0, 0))
            screen.blit(message, (440, 450))
            pygame.display.flip()
            intmessage = ''
            exit = False
            while True:
                bufferchar = get_and_print_message()
                if bufferchar == 'end':
                    if intmessage != '':
                        SoldierNum = int(intmessage)
                    else:
                        continue
                    if SoldierNum <= Player.money:
                        Player.money -= SoldierNum
                        break
                    else:
                        exit = True
                        break
                elif bufferchar is None:
                    continue
                intmessage += bufferchar
                num = mytext.render(intmessage, True, (0, 0, 0))
                screen.blit(num, (440, 500))
                pygame.display.flip()
                bufferchar = None
            if exit:
                continue
            newsoldier = playerSoldier[sver].getnum() + SoldierNum
            playerSoldier[sver].setnum(newsoldier)
            playerSoldier[sver].kind = skind
            playerSoldier[sver].verNum = sver
        pygame.display.flip()


# technology upgrade mode of player
def techupgrade():
    while True:
        refresh()
        mousePress = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePress = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    return
        # print selections on screen
        mytext = pygame.font.SysFont('Comic Sans MS', 50)
        screen.blit(smallwindow, smallwindow_rect)
        tech1 = mytext.render('Soldier Attack', True, (0, 0, 0))
        screen.blit(tech1, (450, 400))
        tech2 = mytext.render('Soldier Speed', True, (0, 0, 0))
        screen.blit(tech2, (450, 480))
        tech3 = mytext.render('Money earn per turn', True, (0, 0, 0))
        screen.blit(tech3, (450, 560))
        mytext = pygame.font.SysFont('Comic Sans MS', 40)
        selected = -1
        # get which technology player select
        x, y = pygame.mouse.get_pos()
        if abs(x - 640) <= 180:
            if abs(y - 420) <= 20:
                selected = 1
                pygame.draw.rect(screen, (255, 255, 0), (440, 390, 380, 50), 5)
            elif abs(y - 500) <= 20:
                selected = 2
                pygame.draw.rect(screen, (255, 255, 0), (440, 470, 380, 50), 5)
            elif abs(y - 580) <= 20:
                selected = 3
                pygame.draw.rect(screen, (255, 255, 0), (440, 550, 380, 50), 5)
        # with mouse button down, upgrade technology
        if mousePress and selected != -1:
            if selected == 1:
                if Player.money < Player.upgradeNeed['attack'] or \
                        Player.tech.soldierAttack >= 2:
                    continue
                else:
                    Player.money -= Player.upgradeNeed['attack']
                    Player.upgradeNeed['attack'] += 100
                    Player.tech.soldierAttack += 0.25
            elif selected == 2:
                if Player.money < Player.upgradeNeed['speed'] or \
                        Player.tech.moveSpeed >= 4:
                    continue
                else:
                    Player.money -= Player.upgradeNeed['speed']
                    Player.upgradeNeed['speed'] += 200
                    Player.tech.moveSpeed += 1
            elif selected == 3:
                if Player.money < Player.upgradeNeed['money']:
                    continue
                else:
                    Player.money -= Player.upgradeNeed['money']
                    Player.tech.moneyperTurn += 500
        pygame.display.flip()


# player turn
# get keyboard input to select mode
def playerTurn():
    # reset all soldier move status
    for s in playerSoldier.keys():
        if playerSoldier[s].getnum() != 0:
            playerSoldier[s].move = False
    # select mode
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    attack()
                    refresh()
                elif event.key == pygame.K_p:
                    produce()
                    refresh()
                elif event.key == pygame.K_e:
                    return
                elif event.key == pygame.K_u:
                    techupgrade()
        pygame.display.flip()


# check who win the game
def Win():
    # check if player soldier enter computer country
    for soldierA in playerSoldier.keys():
        if vertexData[soldierA].isCountry() and \
                vertexData[soldierA].territory == "R" and \
                playerSoldier[soldierA].getnum() > 0:
            return "Player WIN !!"
    # check if computer soldier enter player country
    for soldierB in ComSoldier.keys():
        if vertexData[soldierB].isCountry() and \
                vertexData[soldierB].territory == "L" and \
                ComSoldier[soldierB].getnum() > 0:
            return "Computer WIN"
    return False


# refresh the page
# need to add pygame.display.flip() when needed
def refresh():
    update()
    gameprint()
    drawPic()
    printSoldier()
    screen.blit(information, information_rect)
    infoText = \
        mytext.render('Gold: {0}  Attack: {1}/{2}  Speed: {3}/{4}  Gold Earn: {5}/{6}'.format(
                       Player.money,
                       Player.tech.soldierAttack,
                       Player.upgradeNeed['attack'],
                       Player.tech.moveSpeed,
                       Player.upgradeNeed['speed'],
                       Player.tech.moneyperTurn,
                       Player.upgradeNeed['money']), True, (0, 0, 0))
    screen.blit(counterimage, (210, 200))
    screen.blit(infoText, (320, 75))


if __name__ == "__main__":
    # initiate package and window
    pygame.init()
    pygame.font.init()
    mytext = pygame.font.SysFont('Comic Sans MS', 40)

    size = width, height = 1280, 1080
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)
    # load all picture needed, scale it to needed size
    background = pygame.image.load("map.jpg")
    back_rect = background.get_rect()

    smallwindow = pygame.image.load("smallWindowBack.jpg")
    smallwindow_rect = smallwindow.get_rect()
    smallwindow_rect.move_ip(320, 250)
    smallwindow = pygame.transform.scale(smallwindow, (640, 480))
    soldier_back = pygame.image.load("soldier_back.png")
    soldier_back = pygame.transform.scale(soldier_back, (250, 500))
    archer_image = pygame.image.load("train_archer.png")
    footman_image = pygame.image.load("train_footman.png")
    pikeman_image = pygame.image.load("train_pikeman.png")
    cavalry_image = pygame.image.load("train_cavalry.png")
    soldier_select = [archer_image, footman_image, cavalry_image, pikeman_image]
    archer = pygame.image.load("archer.png")
    footman = pygame.image.load("footman.png")
    pikeman = pygame.image.load("pikeman.png")
    cavalry = pygame.image.load("cavalry.png")
    print_soldier = [archer, footman, cavalry, pikeman]
    lightHouse = pygame.image.load("watchtower.png")
    lightHouse = pygame.transform.scale(lightHouse, (80, 80))
    information = pygame.image.load("information.png")
    information_rect = information.get_rect()
    information_rect.move_ip(270, 0)
    counterimage = pygame.image.load("counter.png")
    counterimage = pygame.transform.scale(counterimage, (150, 150))

    # start page
    startMode()

    # enter the game
    initialData()
    initialPrint()

    roundnum = 100

    # play the game round by round
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        refresh()
        pygame.display.flip()
        # even number player round
        if roundnum % 2 == 0:
            playerTurn()
            Player.money += Player.tech.moneyperTurn
        else:
            Computer()
            Com.money += Com.tech.moneyperTurn
        roundnum -= 1
        # check if someone win and print
        # base on take down other's country
        state = Win()
        if state:
            screen.blit(smallwindow, smallwindow_rect)
            mytext = pygame.font.SysFont('Comic Sans MS', 70)
            winmessage = mytext.render(state, True, (0, 0, 0))
            screen.blit(winmessage, (480, 480))
            pygame.display.flip()
            pygame.time.wait(5000)
            break
        # if the round number is zero, check who take most territories
        elif roundnum == 0:
            countPlayer = 0
            countCom = 0
            for i in LvertexData.keys():
                if LvertexData[i].territory == "L":
                    countPlayer += 1
                else:
                    countCom += 1
            screen.blit(smallwindow, smallwindow_rect)
            mytext = pygame.font.SysFont('Comic Sans MS', 70)
            if countPlayer >= countCom:
                winmessage = mytext.render('Player WIN !!', True, (0, 0, 0))
            else:
                winmessage = mytext.render('Computer WIN', True, (0, 0, 0))
            screen.blit(winmessage, (480, 480))

            pygame.display.flip()
            pygame.time.wait(5000)
        pygame.display.flip()
