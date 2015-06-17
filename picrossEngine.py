"""Picross Engine"""

#Our necessary imports
import pygame, sys

#initialize pygame
pygame.init()

#Declare constants
SCREEN_SIZE = (600,400)
GAME_TITLE = "Picross Engine"

         #R   G   B
WHITE = (255,255,255)
BLACK = (0,  0,  0)
RED =   (255, 0, 0)
GREEN = (0, 255, 0)
BLUE =  (0, 0,   0)

BACKGROUND_COLOR = WHITE

#Set up the game environment
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)
screen.fill(BACKGROUND_COLOR)

#Game Loop variables
exitGame = False

#Here are our game classes
class PicrossStage:
    length = 0
    columns = [[]]
    rows = [[]]
    stage = [[]]
    name = ""
    def __init__(self, length, stage, name):
        self.length = length
        self.stage = stage
        self.name = name
        columns = makeGridColumn(stage)
        rows = makeGridRow(stage)

class PicrossCollection:
    stages = []
    stageNames = []
    def __init__(self, picrossStage):
        self.stages.append(picrossStage)
        self.stageNames.append(picrossStage.name)

    def addStage(self, picrossStage):
        self.stages.append(picrossStage)
        self.stageNames.append(picrossStage.name)
        
    
#Here are our game functions
def makeGridColumn(stage):
    """This function calculates our column hints"""
    for i in stage:
        for j in i:
            print j
def makeGridRow(stage):
    """This function calculates our row hints"""
    rowHint = [[]]
    singleRow = []
    streak = 0
    for i in stage:
        streak = 0
        for index, j in enumerate(i):
            if j==1:
                streak += 1
            else:
                if streak > 0:
                    singleRow.append(streak)
                streak = 0
            if (streak > 0 and (index+1 == len(stage))):
                singleRow.append(streak)
        rowHint.append(singleRow)
        singleRow = []
    rowHint.pop(0)
    for row in rowHint:
        print row
    
def grabStage(path, index):
    """This function returns a stage"""
    searchString = "[Stage %s]\n" % index
    startReading = False
    readCounter = 0
    stageName = ""
    stageLength = 100000
    stage = [[]]
    with open(path) as f:
        for s in f.readlines():
            if startReading:
                if readCounter == 0:
                    stageName = (s.replace("\n",""))
                if readCounter == 1:
                    stageLength = int(s.replace("\n",""))
                if (readCounter > 1 and readCounter <= (stageLength+1)):
                    s = s.replace("\n", "")
                    sList = list(s)
                    stage.append([int(x) for x in sList])
                if readCounter > (stageLength + 1):
                    startReading = False
                readCounter += 1
            else:
                if s == searchString:
                    startReading = True
    """Remove empty element from list"""
    stage.pop(0)

    """Create a new picross stage"""
    return PicrossStage(stageLength,stage,stageName)

#End of GrabStage function
                
                

#GameStart
myCollection = PicrossCollection(grabStage("stages.txt", 5))
for stages in PicrossCollection.stages:
    for stage in stages.stage:
        print stage

#Here is our gameLoop
while not exitGame:
    #Cap our game at 30 fps
    clock.tick(30)

    #Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exitGame = True
    #Display Update
    pygame.display.update()

#Program Exit
pygame.quit()
sys.exit()
