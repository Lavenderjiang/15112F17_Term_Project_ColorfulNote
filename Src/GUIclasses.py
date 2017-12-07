from tkinter import *
import os
from PIL import ImageGrab

def saveImage(canvas,data,dirPath):
    x=data.root.winfo_rootx()+canvas.winfo_x()
    y=data.root.winfo_rooty()+canvas.winfo_y()

    x1=x+data.width*2
    y1=y+data.height*2
    
    path = os.path.join(dirPath,"new.png")
    ImageGrab.grab().crop((x+500,y+50,x1,y1)).save(path)

class button(object):
    ''' 
    Class for switch-mode button.

    @param x: horizontal coord of the center of the button
    @param y: vertical coord of the center of the button (0 on top)
    @param mode: string of the name of the mode to switch to
    @param display: the string to display on button

    Note:
        Button size can be changed by tweaking xs and yxRatio.
        When clicked, the system time is reset.
    
    Usage:
        To activate button, call with bindButton().
    '''
    def __init__(self,x,y,mode,display="button",xs=40,ys =40/4):
        self.xs = xs
        self.ys = ys
        
        self.cx = x
        self.cy = y
        self.text = display
        self.minx = x - xs
        self.miny = y - ys
        self.maxx = x + xs
        self.maxy = y + ys
        self.mode = mode

    def reCalc(self):
        self.minx = self.cx - self.xs
        self.miny = self.cy - self.ys
        self.maxx = self.cx + self.xs
        self.maxy = self.cy + self.ys

    def draw(self,canvas):
        color = "#44d9e6"
        thickness = 2
        canvas.create_rectangle(self.minx,self.miny,self.maxx,self.maxy,
                                fill=color,width=3)
        canvas.create_text(self.cx,self.cy,text=self.text,font="Helvetica 15 bold")

    def onclick(self,data):
        #switch mode and reset time
        if data.mouseX > self.minx and data.mouseX < self.maxx \
        and data.mouseY > self.miny and data.mouseY < self.maxy:
            data.readyForDeltaDraw = False
            #data.canvas.delete("all")
            data.mode = self.mode 
            if data.mode == "create":
                self.stop = False
                #self.rings = []
            data.curTime = 0 

class saveButton(button):
    def onclick(self,data):
        if data.mouseX > self.minx and data.mouseX < self.maxx \
        and data.mouseY > self.miny and data.mouseY < self.maxy:
            if data.saved == True: return
            directory = filedialog.askdirectory()
            #print("NAME!!!",directory)
            saveImage(data.canvas,data,directory)
            data.saved = True

class shareButton(button):
    def onclick(self,data):
        if data.mouseX > self.minx and data.mouseX < self.maxx \
        and data.mouseY > self.miny and data.mouseY < self.maxy:
            if data.shared == True: return
            webbrowser.open("http://google.com")
            data.shared = True

class stopButton(button):
    def onclick(self,data):
        if data.mouseX > self.minx and data.mouseX < self.maxx \
        and data.mouseY > self.miny and data.mouseY < self.maxy:
            data.stop = True

def bindButton(button,data):
    button.draw(data.canvas)
    button.onclick(data)

###################################

def menuInit(data):
    class menuParam: pass
    data.menu = menuParam()
    data.menu.homeButton = button(data.width/4,data.height/4,"home","home")
    data.menu.saveButton = saveButton(data.width/4,data.height/5,"save","save")
    data.menu.shareButton = shareButton(data.width/4,data.height/4,"share","share")
    data.menu.stopButton = stopButton(data.width/4,data.height/4,"stop","stop")
    buttons = [data.menu.homeButton, data.menu.stopButton, data.menu.saveButton, data.menu.shareButton]
    data.createMenu = sideMenu(data,0,0,data.width/6,2*data.height/3,"pink",[1,1,1,1],buttons,20)

class sideMenu(object):
    '''
    Menu object. Take in a list of button and size specification, display
    a menu with all the buttons
    '''
    def __init__(self,data,x0,y0,x1,y1,colors,grid,buttons,space=0):
        self.data = data
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.dy = self.y1-self.y0
        self.grid = grid
        self.space = space
        self.buttons = buttons
        self.init = True

    def drawMenu(self):
        if self.init == True:
            grid = self.grid
            oldY = 0
            xSize = (self.x1 - self.x0)/2
            cx = self.x0 + xSize
            numSpace = len(grid) - 1
            print(grid)
            unitY = (self.dy - numSpace * self.space) / sum(grid)
            for i in range(len(grid)):
                ratio = grid[i]
                nexY = oldY + unitY * ratio
                ySize = (nexY - oldY)/2
                cy = oldY + ySize
                #change button attributes
                print(self.buttons[i])
                print("*******************")
                self.buttons[i].cx = cx
                self.buttons[i].cy = cy
                self.buttons[i].xs = xSize
                self.buttons[i].ys = ySize
                self.buttons[i].reCalc()
                print("old",oldY,"nex",nexY)
                oldY = nexY
        self.init = False
        for button in self.buttons:
            bindButton(button,self.data)

def textRow(canvas,left,right,top,down,texts,color="black"):
    rows = len(texts)
    cx = left + (right - left)/2
    y0 = top
    unitInc = (down - top) / rows
    print("in textRow! rows:",rows)
    for i in range(rows):
        cy = y0 + i *unitInc
        print("creating texts!")
        canvas.create_text(cx,cy,text=texts[i],font="Helvetica 15 bold",fill=color)

###########
def dancingNoteInit(data):
        data.note = PhotoImage(file="note.gif")
        data.bound = [data.width/6, 0, data.width, data.height]
        data.dance = False
        data.dancingHeight = data.height - 75
        data.dy = 7

def verticalJump(data):
    if data.dance == True:
        upperBound = data.height - 100
        lowerBound = data.height - 50 
        data.dancingHeight += data.dy
        if data.dancingHeight < upperBound or data.dancingHeight > lowerBound:
            data.dy = -data.dy
