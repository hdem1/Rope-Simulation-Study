from RopeSimPhysics import Simulator
from RopeUI import Button
import pygame
import pygame.freetype
import numpy as np
import time
import random

def getDistance(pos1, pos2):
    return np.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

pygame.init()
screen_width = 1300
screen_height = 800
screen = pygame.display.set_mode([screen_width, screen_height])

pointDiameter = 25

simulator = Simulator(defaultPointDiameter = pointDiameter, width = screen_width, height=screen_height)


buttons = []
buttons.append(Button(10,10,130,40,label = "Play/Pause", color = [150,100,100], clickedColor = [50,200,50], clickDuration = -1))
buttons.append(Button(160,10,130,40,label = "Clear", clickedColor = [200,50,50]))
buttons.append(Button(310,10,130,40,label = "Eraser", clickedColor = [200,50,50], clickDuration = -1))
buttons.append(Button(460,10,130,40,label = "Stretch", clickedColor = [50,200,50], clickDuration = -1))
buttons.append(Button(10,60,130,40,label = "Simple Rope", clickedColor = [50,200,50]))
buttons.append(Button(160,60,130,40,label = "Generate Cloth", clickedColor = [50,200,50]))
buttons.append(Button(10,110,130,40,label = "Toggle Gravity", clickedColor = [50,200,50], clickDuration = -1))
buttons.append(Button(10,160,130,40,label = "Toggle Constant Wind", clickedColor = [50,200,50], clickDuration = -1))
buttons.append(Button(10,210,130,40,label = "Toggle Variable Wind", clickedColor = [50,200,50], clickDuration = -1))


clicking = False
clickInPoint = -1
mouseClickStart = [0,0]

deleting = False
eraserDiameter = 50

stretching = False

running = True
paused = True

lastUpdate = time.time()
simulationRate = 10
clickingOffset = [0,0]
clickStartTime = 0
clickHoldThreshold = 0.3

forceIndices = [] #gravity, conWind, varWind
gravityOn = True
gravityValue = [0,-10]
if gravityOn:
    forceIndices.append(simulator.addForce(gravityValue))
    buttons[6].click(time.time())
else:
    forceIndices.append(-1)

conWindOn = False
conWindValue = [5, 0]
forceIndices.append(-1)

varWindOn = False
varWindMag = [5,2]
forceIndices.append(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clickStartTime = time.time()
            clicking = True
            mouseClickStart = pygame.mouse.get_pos()
            clickInPoint = -1
            index, dist = simulator.closestPoint(mouseClickStart[0], mouseClickStart[1])
            if dist <= pointDiameter/2:
                clickInPoint = index
                simulator.setClickedIndex(index)
                clickingOffset = np.subtract(simulator.getPointPosition(index), mouseClickStart)
            if clickInPoint == -1:
                for i in range(len(buttons)):
                    if buttons[i].inButton(mouseClickStart[0], mouseClickStart[1]):
                        clickInPoint = -2 - i
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            clickTime = time.time() - clickStartTime
            clicking = False
            mouseClickEnd = pygame.mouse.get_pos()
            if clickInPoint == -1:
                if not deleting and getDistance(mouseClickStart, mouseClickEnd) < pointDiameter/2:
                    simulator.addPoint(mouseClickStart)
            elif clickInPoint == -2 and buttons[0].inButton(mouseClickEnd[0], mouseClickEnd[1]): #PAUSE/PLAY
                buttons[0].click(time.time())
                paused = not paused
                if paused:
                    simulator.pauseSimulation()
                else:
                    lastUpdate = time.time()
                    if stretching:
                        stretching = False
                        buttons[3].click(time.time())
            elif clickInPoint == -3 and buttons[1].inButton(mouseClickEnd[0], mouseClickEnd[1]): #CLEAR SCREEN
                buttons[1].click(time.time())
                simulator.clearScreen()
                if not paused:
                    paused = True
                    buttons[0].click(time.time())
            elif clickInPoint == -4 and buttons[2].inButton(mouseClickEnd[0], mouseClickEnd[1]): #ERASER
                buttons[2].click(time.time())
                deleting = not deleting
            elif clickInPoint == -5 and buttons[3].inButton(mouseClickEnd[0], mouseClickEnd[1]): #STRETCHING
                stretching = not stretching
                buttons[3].click(time.time())
                if stretching:
                    if not paused:
                        paused = True
                        buttons[0].click(time.time()) 
                    if deleting:
                        buttons[2].click(time.time())
                        deleting = False
            elif clickInPoint == -6 and buttons[4].inButton(mouseClickEnd[0], mouseClickEnd[1]): #Generate Cloth
                simulator.clearScreen()
                if not paused:
                    paused = True
                    buttons[0].click(time.time()) 
                num_wide = 10
                w = screen_width * 0.6
                topLeftX = screen_width * 0.2
                topLeftY = screen_height * 0.2
                x = topLeftX
                #Make points:
                for i in range(num_wide):
                    simulator.addPoint([x,topLeftY])
                    x += w/(num_wide-1)
                #Make sticks:
                for i in range(num_wide-1):
                    simulator.addStick(i, i+1)
                #Fasten the corner:
                simulator.changeLockedSetting(0)
            elif clickInPoint == -7 and buttons[5].inButton(mouseClickEnd[0], mouseClickEnd[1]): #Generate Cloth
                simulator.clearScreen()
                if not paused:
                    paused = True
                    buttons[0].click(time.time()) 
                num_wide = 8
                w = screen_width * 0.6
                num_high = 5
                h = screen_height * 0.6
                topLeftX = screen_width * 0.2
                topLeftY = screen_height * 0.2
                x = topLeftX
                y = topLeftY
                #Make points:
                for i in range(num_wide):
                    for j in range(num_high):
                        simulator.addPoint([x,y])
                        y += h/(num_high-1)
                    x += w/(num_wide-1)
                    y = topLeftY
                #Make vertical sticks:
                for i in range(num_wide):
                    for j in range(num_high - 1):
                        simulator.addStick(i*num_high+j, i*num_high+j+1)
                #Make horizontal sticks:
                for i in range(num_wide-1):
                    for j in range(num_high):
                        simulator.addStick(i*num_high+j, (i+1)*num_high+j)
                #Fasten the corners:
                simulator.changeLockedSetting(0)
                simulator.changeLockedSetting((num_wide-1)*num_high)
            elif clickInPoint == -8 and buttons[6].inButton(mouseClickEnd[0], mouseClickEnd[1]): #Toggle Gravity
                buttons[6].click(time.time())
                gravityOn = not gravityOn
                if gravityOn:
                    forceIndices[0] = simulator.addForce(gravityValue)
                else:
                    simulator.removeForce(forceIndices[0])
                    for i in range(len(forceIndices)):
                        if forceIndices[i] > forceIndices[0]:
                            forceIndices[i] -= 1
                    forceIndices[0] = -1
            elif clickInPoint == -9 and buttons[7].inButton(mouseClickEnd[0], mouseClickEnd[1]): #Toggle Constant Wind
                buttons[7].click(time.time())
                conWindOn = not conWindOn
                if conWindOn:
                    forceIndices[1] = simulator.addForce(conWindValue)
                else:
                    simulator.removeForce(forceIndices[1])
                    for i in range(len(forceIndices)):
                        if forceIndices[i] > forceIndices[1]:
                            forceIndices[i] -= 1
                    forceIndices[1] = -1
            elif clickInPoint == -10 and buttons[8].inButton(mouseClickEnd[0], mouseClickEnd[1]): #Toggle Variable Wind
                buttons[8].click(time.time())
                varWindOn = not varWindOn
                if varWindOn:
                    forceIndices[2] = simulator.addForce([0,0])
                else:
                    simulator.removeForce(forceIndices[2])
                    for i in range(len(forceIndices)):
                        if forceIndices[i] > forceIndices[2]:
                            forceIndices[i] -= 1
                    forceIndices[2] = -1
            elif clickInPoint >= 0 and not deleting:
                simulator.removeClickedIndex()
                index, dist = simulator.closestPoint(mouseClickEnd[0], mouseClickEnd[1])
                if index == clickInPoint and dist < pointDiameter/2:
                    if clickTime < clickHoldThreshold:
                        simulator.changeLockedSetting(index)
                elif index >= 0 and dist < pointDiameter:
                    simulator.addStick(index, clickInPoint)
                

            #if (mouseClickEnd.dist(mouseClickStart) < pointDiameter/2):
    

    # Fill the background with white
    screen.fill((255, 255, 255))

    #Simulate:
    if not paused:
        newLastUpdate = time.time()
        simulator.simulate((newLastUpdate - lastUpdate)*simulationRate, 10)
        lastUpdate = newLastUpdate
        if varWindOn:
            simulator.modifyForce(forceIndices[2],[(1-2*random.random()) * varWindMag[0]/5, (1-2*random.random()) * varWindMag[1]/5], limits = varWindMag)
    
    # Draw points:
    simulator.drawSimulation(screen, screen_width, screen_height)

    # Draw/Do mouseStuff
    if clicking:
        mousePos = pygame.mouse.get_pos()
        if deleting:
            if clickInPoint >= -1:
                pygame.draw.circle(screen, (0,0,0), (mousePos[0], mousePos[1]), eraserDiameter/2, width = 1)
                index, dist = simulator.closestPoint(mousePos[0], mousePos[1])
                while dist < eraserDiameter/2 + pointDiameter/2:
                    simulator.removePoint(index)
                    index, dist = simulator.closestPoint(mousePos[0], mousePos[1])
                index, dist = simulator.closestStick(mousePos[0], mousePos[1])
                while dist < eraserDiameter/2:
                    simulator.removeStick(index)
                    index, dist = simulator.closestStick(mousePos[0], mousePos[1])
        elif clickInPoint == -1:
            if getDistance(mousePos, mouseClickStart) < pointDiameter / 2:
                pygame.draw.circle(screen, (0,0,255), (mouseClickStart[0], mouseClickStart[1]), pointDiameter/2)
            else: 
                pygame.draw.line(screen, (255,0,0), (mouseClickStart[0], mouseClickStart[1]), (mousePos[0], mousePos[1]))
        elif clickInPoint >= 0:
            if paused and not stretching:
                index, dist = simulator.closestPoint(mousePos[0], mousePos[1])
                if dist > pointDiameter/2:
                    originLocation = simulator.getPointPosition(clickInPoint)
                    pygame.draw.line(screen, (0,0,255), (originLocation[0], originLocation[1]), (mousePos[0], mousePos[1]))
                elif index != clickInPoint:
                    originLocation = simulator.getPointPosition(clickInPoint)
                    destLocation = simulator.getPointPosition(index)
                    pygame.draw.line(screen, (0,0,255), (originLocation[0], originLocation[1]), (destLocation[0], destLocation[1]))
            else:
                if stretching:
                    simulator.updateClickedIndex(mousePos + clickingOffset, maintainLength = False)
                else:
                    simulator.updateClickedIndex(mousePos + clickingOffset)





    # Draw Buttons:
    for i in range(len(buttons)):
        if i != 3 or paused:
            buttons[i].draw(screen,time.time())

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()