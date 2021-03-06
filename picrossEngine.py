"""Picross Engine"""

#Our necessary imports
import pygame, sys

#initialize pygame
pygame.init()

#Declare constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SCREEN_SIZE = (SCREEN_WIDTH,SCREEN_HEIGHT)
GAME_TITLE = "Picross Engine"
FRAME_RATE = 30

         #R   G   B
WHITE = (255,255,255)
BLACK = (0,  0,  0)
RED =   (255, 0, 0)
GREEN = (0, 255, 0)
BLUE =  (0, 0,   255)

GAME_FONT = "monospace"
FONT_SIZE = 15
HINT_FONT_SIZE = 12

BACKGROUND_COLOR = WHITE

BACKGROUND_FILE = "lib/background.jpg"
X_FILE = "lib/x.png"
GAME_ICON_FILE = "lib/game_icon.png"

BOX_WIDTH = 15

#Set up the game environment
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)
screen.fill(BACKGROUND_COLOR)
background = pygame.image.load(BACKGROUND_FILE).convert()
x_marker = pygame.image.load(X_FILE).convert_alpha()
game_icon = pygame.image.load(GAME_ICON_FILE).convert_alpha()
pygame.display.set_icon(game_icon)

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
        self.columns = makeGridColumn(stage)
        self.rows = makeGridRow(stage)

class PicrossCollection:
    stages = []
    stageNames = []
    def __init__(self, picrossStage):
        self.stages.append(picrossStage)
        self.stageNames.append(picrossStage.name)

    def addStage(self, picrossStage):
        self.stages.append(picrossStage)
        self.stageNames.append(picrossStage.name)

class Box:
    width = 0
    enabled = False
    locationX = 0
    locationY = 0
    boxSprite = None 
    def __init__(self, width, locationX, locationY, enabled):
        self.width = width
        self.enabled = enabled
        self.locationX = locationX
        self.locationY = locationY
        self.boxSprite = pygame.Rect(self.locationX, self.locationY, self.width, self.width)
    def enable(self):
        self.enabled = True
    
#Here are our game functions
def makeGridColumn(stage):
    """This function calculates our column hints"""

    """Make a flipped version of stage"""
    newStage = [[]]
    column=[]
    for k in range(len(stage)):
        column = []
        for j in stage:
            column.append(j[k])
        newStage.append(column)
    newStage.pop(0)
    """And now the code is pretty much the same as makeGridRow"""
    columnHint = [[]]
    singleColumn = []
    streak = 0
    for i in newStage:
        streak = 0
        for index,j in enumerate(i):
            if j==1:
                streak += 1
            else:
                if streak > 0:
                    singleColumn.append(streak)
                streak = 0
            if (streak > 0 and (index+1 == len(newStage))):
                singleColumn.append(streak)
        columnHint.append(singleColumn)
        singleColumn = []
    columnHint.pop(0)
    return columnHint
    
            
            
            
#End of makeGridColumn function
            
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
    return rowHint
    
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

#This function will simplify the label making process
def drawLabel(font, size, color, text, location):
    """Use the global screen"""
    global screen
    myFont = pygame.font.SysFont(font, size)
    myLabel = myFont.render(text,1,color)
    screen.blit(myLabel, location)
    

#Draw Stage Function
def drawStage(picrossCollection, index, solution, clickSet):
    """Let's blit the background to the screen first"""
    screen.blit(background,(0,0))
    """Here we write a label to the screen displaying the stage name      -                                                                 NAME LOCATION"""
    drawLabel(GAME_FONT, FONT_SIZE, BLACK, ("Stage: %s" % picrossCollection.stages[index].name),(int(SCREEN_WIDTH*.392),(int(SCREEN_HEIGHT*.1175))))
    """Let's declare some shortcut variables to make this process easier"""
    tempStage = picrossCollection.stages[index]
    tempGrid = []
    """Here we set the location of the puzzle depending on the size"""
    tempStartingPointX = 0
    tempStartingPointY = 0
    if (tempStage.length == 5):
        tempStartingPointX = (SCREEN_WIDTH * .43)
        tempStartingPointY = (SCREEN_HEIGHT * .47)
    elif (tempStage.length == 10):
        tempStartingPointX = (SCREEN_WIDTH * .36)
        tempStartingPointY = (SCREEN_HEIGHT * .39)
    else:
        tempStartingPointX = (SCREEN_WIDTH * .375)
        tempStartingPointY = (SCREEN_HEIGHT * .3125)

    """Here we print the row/column hints to the screen"""
    """ROW"""
    for i in range(tempStage.length):
            tempStr = str(tempStage.rows[i]).replace("[","").replace("]","").replace(","," ")
            #This tempStrSize variable helps us measure the width of the string, to help us offset the text and get it as close as possible to the grid
            tempStrSize = pygame.font.SysFont(GAME_FONT,HINT_FONT_SIZE).size(tempStr)[0]
            tempColor = BLACK
            #This if statement adds the help marker on the current row
            if (pygame.mouse.get_pos()[1] >((tempStartingPointY+BOX_WIDTH) + (i*BOX_WIDTH)) and pygame.mouse.get_pos()[1] < ((tempStartingPointY+BOX_WIDTH) + ((i+1)*BOX_WIDTH))):
                 drawLabel(GAME_FONT,HINT_FONT_SIZE,BLACK,">",((tempStartingPointX * .99), tempStartingPointY + (BOX_WIDTH * (i+1))))
            if (i % 2 == 0):
                tempColor = BLUE
            else:
                tempColor = RED
            drawLabel(GAME_FONT,HINT_FONT_SIZE,tempColor,tempStr,(tempStartingPointX * .94 - tempStrSize + (BOX_WIDTH/2),(tempStartingPointY+BOX_WIDTH) + (i*BOX_WIDTH)) )
    """COLUMN"""
    for i in range(tempStage.length):
             tempStr = str(tempStage.columns[i]).replace("[","").replace("]","").replace(",","\n").replace(" ","")
             tempCount = tempStr.count('\n')+1
             tempStrSize = tempCount * BOX_WIDTH
             tempColor = BLACK
             #This if statement adds the help marker on the current column
             if (pygame.mouse.get_pos()[0] >((tempStartingPointX+BOX_WIDTH) + (i*BOX_WIDTH)) and pygame.mouse.get_pos()[0] < ((tempStartingPointX+BOX_WIDTH) + ((i+1)*BOX_WIDTH))):
                 drawLabel(GAME_FONT,HINT_FONT_SIZE,BLACK,"V",((tempStartingPointX+BOX_WIDTH) + (i*BOX_WIDTH), tempStartingPointY * .99))
             if (i % 2 == 0):
                 tempColor = BLUE
             else:
                tempColor = RED
             for j in range(tempCount):
                 tempStrList = tempStr.split('\n')
                 drawLabel(GAME_FONT,HINT_FONT_SIZE,tempColor,tempStrList[j],((tempStartingPointX+BOX_WIDTH) + (i*BOX_WIDTH),tempStartingPointY * .95 - tempStrSize + (BOX_WIDTH/2) + (j*BOX_WIDTH)))

    tempGrid2 = [[]]
    """TEMPORARY - HERE WE ENABLE THE SQUARES"""
    for i in range(tempStage.length):
        for j in range(tempStage.length):
            enabled = False
            if (tempStage.stage[i][j] == 1):
                enabled = True
            """Here we create our boxes and add them to the grid"""
            tempGrid.append(Box(BOX_WIDTH,(((j+1)*BOX_WIDTH)+tempStartingPointX),(((i+1)*BOX_WIDTH)+tempStartingPointY), enabled))
            enabled = False
        tempGrid2.append(tempGrid)
        tempGrid = []
    tempGrid2.pop(0)
    """Now let's draw us some boxes!"""
    for indexI,i in enumerate(tempGrid2):
        for indexJ,j in enumerate(i):
            tempWidth = 1
            if (j.enabled and clickSet[indexI][indexJ] == 1):
                tempWidth = 0
            elif (clickSet[indexI][indexJ] == 1):
                clickSet[indexI][indexJ] = 0
            elif (clickSet[indexI][indexJ] == 2):
                screen.blit(x_marker,(j.locationX,j.locationY))
            pygame.draw.rect(screen, BLACK, j.boxSprite,tempWidth)
            tempWidth = 1
    solutionGrid = tempGrid2
    return solutionGrid

#GameSetup function
def gameSetup(collection, index):
    tempClickSet = [[]]
    tempClickSet2 = []
    for i in range(collection.stages[index].length):
        for j in range(collection.stages[index].length):
            tempClickSet2.append(0)
        tempClickSet.append(tempClickSet2)
        tempClickSet2 = []
    tempClickSet.pop(0)
    return tempClickSet

#Click handler - A left click is the value 1, and a right click is the value 2
def clickHandler(gameState, leftOrRight, mousePosition, clickSet, solution):
    if gameState == "game":
        for i in range(len(clickSet)):
            for j in range(len(clickSet)):
                if (solution[i][j].boxSprite.collidepoint(mousePosition)):
                    if (clickSet[i][j] == 0):
                        clickSet[i][j] = leftOrRight
                    elif (clickSet[i][j] == 2):
                        if (leftOrRight == 2):
                            clickSet[i][j] = 0
                    print "clicked on %s,%s" % (i,j) 
    else:
        print "Not in game"
    return clickSet

#GameStart
"""THIS WILL BE A LOOP IN THE FUTURE"""
myCollection = PicrossCollection(grabStage("stages.txt", 1))
myCollection.addStage(grabStage("stages.txt", 2))
myCollection.addStage(grabStage("stages.txt", 3))
myCollection.addStage(grabStage("stages.txt", 4))
myCollection.addStage(grabStage("stages.txt", 5))
myCollection.addStage(grabStage("stages.txt", 6))
myCollection.addStage(grabStage("stages.txt", 7))
myCollection.addStage(grabStage("stages.txt", 8))
myCollection.addStage(grabStage("stages.txt", 9))
myCollection.addStage(grabStage("stages.txt", 10))
myCollection.addStage(grabStage("stages.txt", 11))
myCollection.addStage(grabStage("stages.txt", 12))
myCollection.addStage(grabStage("stages.txt", 13))
myCollection.addStage(grabStage("stages.txt", 14))
myCollection.addStage(grabStage("stages.txt", 15))
myCollection.addStage(grabStage("stages.txt", 16))
myCollection.addStage(grabStage("stages.txt", 17))
myCollection.addStage(grabStage("stages.txt", 18))
myCollection.addStage(grabStage("stages.txt", 19))
myCollection.addStage(grabStage("stages.txt", 20))
#This index will be the current stage in our stage collection
CURRENT_STAGE = 9
#This variable keeps track of which boxes have been clicked
clickSet = [[]]
solutionGrid = []
setup = True
#GameState
GAME_STATE = "game"
#this variable keeps track of whether the left mouse button is up or down
leftDown = False

#Here is our gameLoop
while not exitGame:
    #Cap the game frame rate
    clock.tick(FRAME_RATE)

    #Do some setup related things
    if setup:
        clickSet = gameSetup(myCollection,CURRENT_STAGE-1)
        setup = False

    #Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exitGame = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if CURRENT_STAGE > 1:
                    CURRENT_STAGE -= 1
                    clickSet = gameSetup(myCollection,CURRENT_STAGE-1)
                    setup=True
            elif event.key == pygame.K_RIGHT:
                if CURRENT_STAGE < len(myCollection.stages):
                    CURRENT_STAGE += 1
                    clickSet = gameSetup(myCollection,CURRENT_STAGE-1)
                    setup = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3: #Right Click
                clickSet = clickHandler(GAME_STATE, 2, pygame.mouse.get_pos(),clickSet, solutionGrid)
            else: #Left Click
                leftDown = True
                clickSet = clickHandler(GAME_STATE, 1, pygame.mouse.get_pos(),clickSet, solutionGrid)
        if event.type == pygame.MOUSEBUTTONUP:
            if (leftDown and event.button == 1):
                leftDown = False

    #If our left mouse button is down
    if (leftDown):
        clickSet = clickHandler(GAME_STATE, 1, pygame.mouse.get_pos(),clickSet, solutionGrid)

    #Draw our stage
    solutionGrid = drawStage(myCollection,CURRENT_STAGE-1, solutionGrid, clickSet)
            
    #Display Update
    pygame.display.update()

#Program Exit
pygame.quit()
sys.exit()
