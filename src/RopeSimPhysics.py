from xmlrpc.client import MAXINT
import numpy as np
import random
import pygame


class Point:
    def __init__(self, x, y, locked, diameter, bouncingFactor = 0.8):
        self.pos = [x,y]
        self.lastPos = [x,y]
        self.locked = locked
        self.diameter = diameter
        self.bouncingFactor = bouncingFactor
        self.clicked = False
    def __init__(self, pos, locked, diameter, bouncingFactor = 0.8):
        self.pos = pos
        self.lastPos = pos
        self.locked = locked
        self.diameter = diameter
        self.bouncingFactor = bouncingFactor
        self.clicked = False
    def distToPoint(self, other):
        return np.sqrt((self.pos[0] - other.pos[0])**2 + (self.pos[1] - other.pos[1])**2)
    def dist(self, x, y):
        return np.sqrt((self.pos[0] - x)**2 + (self.pos[1] - y)**2)
    def offScreen(self, width, height):
        if self.pos[0] - self.diameter/2 < 0 or self.pos[0] + self.diameter/2 > width:
            return True
        if self.pos[1] - self.diameter/2 < 0 or self.pos[1] + self.diameter/2 > height:
            return True
        return False
    def putOnScreen(self, width, height):
        flippingXVel = False
        flippingYVel = False
        if self.bouncingFactor > 0:
            offScreen = self.offScreen(width,height)
            if offScreen: 
                prevVel = np.subtract(self.pos, self.lastPos)
                if self.pos[0] - self.diameter/2 < 0 or self.pos[0] + self.diameter/2 > width:
                    flippingXVel = True
                if self.pos[1] - self.diameter/2 < 0 or self.pos[1] + self.diameter/2 > height:
                    flippingYVel = True
        self.pos[0] = max(self.diameter/2,self.pos[0])
        self.pos[0] = min(width-self.diameter/2,self.pos[0])
        self.pos[1] = max(self.diameter/2,self.pos[1])
        self.pos[1] = min(height-self.diameter/2,self.pos[1])
        if flippingXVel:
            self.lastPos[0] = self.pos[0] + prevVel[0] * self.bouncingFactor
        if flippingYVel:
            self.lastPos[1] = self.pos[1] + prevVel[1] * self.bouncingFactor
    def drawPoint(self, screen):
        if self.locked:
            color = (255,0,0)
        else:
            color = (0,0,255)
        pygame.draw.circle(screen, color, (self.pos[0], self.pos[1]), self.diameter/2)

class Stick:
    def __init__(self, a, b):
        self.pointA = a
        self.pointB = b
        self.length = a.distToPoint(b)
    def drawStick(self, screen):
        pygame.draw.line(screen, (0,0,255), (self.pointA.pos[0], self.pointA.pos[1]), (self.pointB.pos[0], self.pointB.pos[1]))
    def resetLength(self):
        self.length = self.pointA.distToPoint(self.pointB)
    def shortestDistance(self, pos):
        lineVector = np.subtract(self.pointB.pos, self.pointA.pos)
        #If the point is on the A side:
        if np.dot(np.subtract(pos, self.pointA.pos), lineVector) <= 0:
            return np.sqrt((pos[0]-self.pointA.pos[0])**2 + (pos[1]-self.pointA.pos[1])**2)

        #If the point is on the B side:
        if np.dot(np.subtract(pos, self.pointB.pos), lineVector) >= 0:
            return np.sqrt((pos[0]-self.pointB.pos[0])**2 + (pos[1]-self.pointB.pos[1])**2)
            
        #Else:
        return abs(np.cross(lineVector, np.subtract(pos, self.pointA.pos))) /self.pointA.distToPoint(self.pointB)


class Simulator:
    def __init__(self, defaultPointDiameter = 25, width = MAXINT, height = MAXINT):
        self.points = []
        self.sticks = []
        self.forces = []
        self.defaultPointDiameter = defaultPointDiameter
        self.width = width
        self.height = height
        self.clickedIndex = -1

    def addPoint(self, position, locked = False, diameter = -1):
        pos = [float(position[0]), float(position[1])]
        if diameter == -1:
            self.points.append(Point(pos,locked, self.defaultPointDiameter))
        else:
            self.points.append(Point(pos,locked, diameter))
    
    def addStick(self, i1, i2):
        self.sticks.append(Stick(self.points[i1],self.points[i2]))

    def addForce(self, fVec):
        self.forces.append(fVec)
        return len(self.forces)-1

    def simulate(self, deltaT, stickIterations):
        for p in self.points:
            if not p.locked and not p.clicked:
                lastPosition = p.pos
                prevVel = np.subtract(p.pos, p.lastPos)
                p.pos = np.add(p.pos, prevVel)
                for f in self.forces:
                    p.pos[0] = float(p.pos[0]) + f[0] * deltaT* deltaT
                    p.pos[1] = float(p.pos[1]) - f[1] * deltaT* deltaT
                p.lastPos = lastPosition
                p.putOnScreen(self.width, self.height)
        
        for j in range(stickIterations):
            indices = []
            for i in range(len(self.sticks)):
                indices.append(i)
            random.shuffle(indices)
            for i in indices:
                stick = self.sticks[i]
                stickCenter = np.add(stick.pointA.pos, stick.pointB.pos)
                stickCenter[0] /= 2
                stickCenter[1] /= 2
                stickDirection = np.subtract(stick.pointA.pos, stick.pointB.pos)
                dirMag = np.sqrt(stickDirection[0]**2 + stickDirection[1]**2) / (stick.length / 2)
                stickDirection[0] = stickDirection[0] / dirMag
                stickDirection[1] = stickDirection[1] / dirMag
                if not stick.pointA.locked and not stick.pointA.clicked:
                    stick.pointA.pos = np.add(stickCenter, stickDirection)
                    stick.pointA.putOnScreen(self.width, self.height)
                if not stick.pointB.locked and not stick.pointB.clicked:
                    stick.pointB.pos = np.subtract(stickCenter, stickDirection)
                    stick.pointB.putOnScreen(self.width, self.height)
    
    def closestPoint(self,x,y):
        min = MAXINT
        minIndex = -1
        for i in range(len(self.points)):
            d = self.points[i].dist(x,y)
            if (d < min):
                min = d
                minIndex = i
        return minIndex, min
    
    def closestStick(self,x,y):
        min = MAXINT
        minIndex = -1
        for i in range(len(self.sticks)):
            d = self.sticks[i].shortestDistance([x,y])
            if (d < min):
                min = d
                minIndex = i
        return minIndex, min

    def pauseSimulation(self):
        for p in self.points:
            p.lastPos = p.pos

    def drawSimulation(self, screen, width, height):
        for s in self.sticks:
            s.drawStick(screen)
        
        for p in self.points:
            p.drawPoint(screen)
        
        totalForce = [0, 0]
        for f in self.forces:
            totalForce[0] += f[0]
            totalForce[1] -= f[1]
        if totalForce != [0, 0]:
            startingPoint = [width/10, height * 5/6]
            scaleFactor = 10
            endPoint = [startingPoint[0] + totalForce[0]*scaleFactor, startingPoint[1] + totalForce[1]*scaleFactor]
            triangleSize = 20
            forceMag = np.sqrt(totalForce[0]**2 + totalForce[1]**2)
            triangleBasePos = [0, 0]
            triangleBasePos[0] = endPoint[0] - float(totalForce[0]) / forceMag * triangleSize
            triangleBasePos[1] = endPoint[1] - float(totalForce[1])  / forceMag * triangleSize
            perpVec = np.cross([0,0,1/forceMag], totalForce)
            perpVec = [perpVec[0] * triangleSize / 3, perpVec[1] * triangleSize / 3]
            pygame.draw.line(screen, (0,0,0), startingPoint, endPoint)
            pygame.draw.polygon(screen, (255, 0, 0), [endPoint, np.add(triangleBasePos,perpVec), np.subtract(triangleBasePos, perpVec)])
    
    def changeLockedSetting(self, index):
        self.points[index].locked = not self.points[index].locked
        self.points[index].lastPos = self.points[index].pos

    def getPointPosition(self,index):
        return self.points[index].pos

    def setClickedIndex(self,index):
        self.clickedIndex = index
        self.points[index].clicked = True

    def updateClickedIndex(self, pos, maintainLength = True):
        if (self.clickedIndex != -1):
            self.points[self.clickedIndex].pos = pos
            self.points[self.clickedIndex].lastPos = pos
            if not maintainLength:
                for s in self.sticks:
                    s.resetLength()
    
    def removeClickedIndex(self):
        if self.clickedIndex != -1:
            self.points[self.clickedIndex].clicked = False 
            self.clickedIndex = -1
    
    def clearScreen(self):
        self.points = []
        self.sticks = []
    
    def removePoint(self, index):
        i, distance = self.closestStick(self.points[index].pos[0],self.points[index].pos[1])
        while (distance < self.points[index].diameter/2):
            self.removeStick(i)
            i, distance = self.closestStick(self.points[index].pos[0],self.points[index].pos[1])
        self.points.pop(index)
    
    def removeStick(self,index):
        self.sticks.pop(index)
    
    def removeForce(self, index):
        return self.forces.pop(index)
    
    def modifyForce(self, index, val, limits = [MAXINT, MAXINT]):
        self.forces[index] = np.add(self.forces[index], val)
        if abs(self.forces[index][0]) > limits[0]:
            self.forces[index][0] = limits[0] * self.forces[index][0] / abs(self.forces[index][0])
        if abs(self.forces[index][1]) > limits[1]:
            self.forces[index][1] = limits[1] * self.forces[index][1] / abs(self.forces[index][1])