import pygame

class Button:
    def __init__(self, x, y, width, height, label="", color = [200, 200, 200], clickedColor = [255,0,0], clickDuration = 0.3, \
                borderColor = [0,0,0], textColor = [0,0,0], fontSize = 12, borderWidth = 5):
        self.topLeft = [x,y]
        self.width = width
        self.height = height
        self.label = label
        self.color = pygame.Color(color)
        self.clickedColor = pygame.Color(clickedColor)
        self.clicked = False
        self.clickReleaseTime = 0
        self.clickDuration = clickDuration
        self.borderColor = pygame.Color(borderColor)
        self.textColor = pygame.Color(textColor)
        self.fontSize = fontSize
        self.borderWidth = borderWidth
    def inButton(self, x, y):
        if x >= self.topLeft[0] and x <= self.topLeft[0] + self.width:
            if y >= self.topLeft[1] and y <= self.topLeft[1] + self.height:
                return True
        return False
    def click(self, time):
        if self.clickDuration >= 0:
            self.clicked = True
            self.clickReleaseTime = time + self.clickDuration 
        else:
            self.clicked = not self.clicked
    def draw(self, screen, time):
        if self.clicked and self.clickDuration >= 0 and time > self.clickReleaseTime:
            self.clicked = False

        pygame.draw.rect(screen, self.borderColor, pygame.Rect(self.topLeft[0], self.topLeft[1], self.width, self.height))
        if self.clicked:
            pygame.draw.rect(screen, self.clickedColor, pygame.Rect(self.topLeft[0]+self.borderWidth, self.topLeft[1]+self.borderWidth, self.width-2*self.borderWidth, self.height-2*self.borderWidth))
        else:
            pygame.draw.rect(screen, self.color, pygame.Rect(self.topLeft[0]+self.borderWidth, self.topLeft[1]+self.borderWidth, self.width-2*self.borderWidth, self.height-2*self.borderWidth))
        font = pygame.font.SysFont('arial', self.fontSize)
        text = font.render(self.label, True, self.textColor)
        xVal = self.topLeft[0]+self.width/2-len(self.label)*self.fontSize/4
        yVal = self.topLeft[1]+self.height/2-self.fontSize/2
        screen.blit(text, [xVal, yVal])