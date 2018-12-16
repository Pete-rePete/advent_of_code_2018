# Advent of Code, day 15
from collections import deque
from time import sleep

def neighbourCells(pos):
    y = pos[0]
    x = pos[1]
    return ((y+1, x), (y, x-1), (y, x+1), (y-1, x))


def readingOrder(pos):
    return (pos[0], pos[1])

class nothingToAttack(Exception):
    pass

class elfDeath(Exception):
    pass

class Unit():
    def __init__(self, faction, position, strength):
        assert (faction == 'G' or faction == 'E'), "must be (E)lf or (G)oblin"
        self.faction  = faction
        self.health = 200
        self.attackPower = strength
        self.pos = position
        self.isAlive = True

    
    def tryToMove(self, eGrid, units, condition=False):
        aliveUnits = [u for u in units if u.isAlive]
        enemies = [e for e in aliveUnits if e.faction != self.faction]
        if not enemies:
            raise nothingToAttack
        #condition = units[2] == self # DEBUGGING CODE currently monitoring goblin2
        occupiedCells = [u.pos for u in aliveUnits if u !=self]
        targetSpots = []
        if condition:
            print('I am in position ' + str(self.pos))
            print('my enemies are in ' + str([e.pos for e in enemies]))
            print('occupied cells: ' + str(occupiedCells))
        
        for e in enemies:
            targets = neighbourCells(e.pos)
            targetSpots.extend([t for t in targets if eGrid[t] == '.' and t not in occupiedCells])
        closestTargets = self.findClosest(eGrid, self.pos, occupiedCells, targetSpots, False)# debugging arg condition (end one)
        # if no targets are accessible, then closestTargets should be empty list
        if condition:# DEBUGGING CODE
            print('my targets are in coordinates ' + str(closestTargets))# DEBUGGING CODE
        if closestTargets:
            # Note, closest target may be adjacent, requiring no movement.
            closestTargets = sorted(closestTargets, key=lambda t: readingOrder(t[0]))
            targetPos, targetDistance = closestTargets[0]
            if targetDistance > 0:
                self.moveTowardsTarget(eGrid, occupiedCells, targetPos, condition)# debugging arg condition
        if condition:# DEBUGGING CODE
            print('I moved to ' + str(self.pos))# DEBUGGING CODE
            

    def findClosest(self, eGrid, startPos, occupiedCells, targets, condition):# debugging arg condition
        q = deque(((startPos,0),))
        foundDist = None
        seen = set()
        closest = []
        while q:
            checkPos, dist = q.popleft()
            if foundDist is not None and dist > foundDist:
                return closest
            if checkPos in seen:
                continue
            seen.add(checkPos)
            if checkPos in occupiedCells or eGrid[checkPos] != '.':
                continue
            if checkPos in targets:
                if condition:
                    print('position ' + str(checkPos) + ', foundDist = ' + str(foundDist) + ", dist = "+str(dist))
                closest.append((checkPos, dist))
                foundDist = dist
            for n in neighbourCells(checkPos):
                # nice outward-expanding bubble :)
                if n not in seen:
                    # all entries at dist will complete before any entries at 
                    #   dist+1 begin being evaluated
                    q.append((n, dist + 1))
        return closest

        
    def moveTowardsTarget(self, eGrid, occupiedCells, targetPos, condition):
        possibleMoves = [x for x in neighbourCells(self.pos) if eGrid[x] == '.' and x not in occupiedCells]
        if condition:
            print('My possible moves are ' + str(possibleMoves))
        if possibleMoves:
            evaluatedMoves = []
            for mp in possibleMoves:
                positions = self.findClosest(eGrid, mp, occupiedCells, [targetPos], condition) # debugging arg condition
                if positions:
                    _,dist = positions[0]
                    evaluatedMoves.append([mp, dist])
            # sort first by distance then by readingOrder
            evaluatedMoves = sorted(evaluatedMoves, key = lambda c: (c[1], *readingOrder(c[0])))
            if condition:
                print('My possible moves are ' + str(evaluatedMoves))
            chosenMove, _ = evaluatedMoves[0]
            self.pos = chosenMove

        return None

    def tryToAttack(self, eGrid, units):
        enemies = [u for u in units if u.faction != self.faction and u.isAlive]
        possibleTargets = [x for x in neighbourCells(self.pos) if eGrid[x] == '.' and x in [i.pos for i in enemies]]
        if possibleTargets:
            possibleEnemies = [e for e in enemies if e.pos in possibleTargets]
            possibleEnemies = sorted(possibleEnemies, key=lambda e: (e.health, *readingOrder(e.pos)))
            targetEnemy = possibleEnemies[0]
            targetEnemy.hasBeenAttacked(self.attackPower)

    def hasBeenAttacked(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.isAlive = False
            if self.faction == 'E':
                raise elfDeath

    def takeTurn(self, eGrid, units):
        if self.isAlive:
            self.tryToMove(eGrid, units)
            self.tryToAttack(eGrid, units)

    def __str__(self):
        return self.faction
    
    def __repr__(self):
        return self.faction


def renderBoard(eGrid, units, round):
    aliveUnits = [u for u in units if u.isAlive]
    allCoords = eGrid.keys()
    ys,xs = zip(*allCoords)
    board = []
    for y in range(max(ys) + 1):
        row = []
        for x in range(max(xs) + 1):
            row.append(eGrid[y,x])
        board.append(row)
    for u in aliveUnits:
        y,x = u.pos
        board[y][x] = str(u)
    
    
    print('ROUND '+ str(round) + '\n' + '\n'.join([''.join(i) for i in board]) + '\n')

def main(elfAP):
    with open('day15.txt') as f:
        sMap = f.read()
    eGrid = {}
    units = []
    # initialize the grid
    for y, line in enumerate(sMap.split('\n')):
        for x, c in enumerate(list(line)):
            if c == 'E':
                units.append(Unit(c,(y,x), strength=elfAP))
                eGrid[(y,x)] = '.'
            elif c == 'G':
                units.append(Unit(c,(y,x), strength=3))
                eGrid[(y,x)] = '.'
            else:
                eGrid[(y,x)] = c
    #begin sim
    i=0
    while len(set([u.faction for u in units if u.isAlive]))>1:
        try:
            for unit in sorted(units, key=lambda c: readingOrder(c.pos)):
                unit.takeTurn(eGrid, units)
            i+=1
            #renderBoard(eGrid, units, round)
        except nothingToAttack:
            print('NOTHING TO ATTACK!')
            break
    winningFaction = [u.faction for u in units if u.isAlive][0]
    finalScore = sum(u.health for u in units if u.faction == winningFaction and u.isAlive) * i
    return False, finalScore, winningFaction

if __name__ == '__main__':
    # Iterate to get the correct AP
    elfAP=1
    failure=True
    while failure:
        try:
            failure, finalScore, winningFaction = main(elfAP)
        except:
            elfAP+=1

    print('final elf attack power: ' + str(elfAP))
    print('final score ' + str(finalScore))
    print(winningFaction)

