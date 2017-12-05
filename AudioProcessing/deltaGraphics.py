# deltaGraphicsDemo2.py

# Fast version of deltaGraphicsDemo1.py
# This time, using delta graphics.

# Displays lots (~5000) random rectangles that do
# not move.

# Then moves an oval over the top of them.  Also changes
# the oval's size and color to show that we can.

# Only delta updated the oval, not the rectangles

from tkinter import *
import random

####################################
# customize these functions
####################################

def drawRectangles(canvas, data):
    for (left, top, right, bottom, color) in data.rects:
        canvas.create_rectangle(left, top, right, bottom, fill=color)

def drawOval(canvas, data):
    left = data.ovalX % 400
    width = 5 + left // 5
    color = hexColor(left * 255// 400, left * 255// 400, 0)
    data.oval = canvas.create_oval(left, 250, left+width, 300, fill=color)
    

def deltaDrawOval(canvas, data):
    left = data.ovalX % 400
    width = 5 + left // 5   
    color = hexColor(left * 255// 400, left * 255// 400, 0)
    # change oval's bounds
    canvas.coords(data.oval, (left, 250, left+width, 300) )
    # change oval's color
    canvas.itemconfig(data.oval, fill=color)

def redrawAll(canvas, data):
    drawRectangles(canvas, data)
    drawOval(canvas, data)

def deltaDraw(canvas, data):
    deltaDrawOval(canvas, data)

def timerFired(data):
    data.ovalX += 10

def hexColor(red, green, blue):
    return ("#%02x%02x%02x" % (red, green, blue))

def randomColor():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return hexColor(red, green, blue)

def init(data):
    data.rects = []
    rectCount = 5000
    for i in range(rectCount):
        left = random.randint(0,450)
        right = left + random.randint(5,50)
        top = random.randint(0,450)
        bottom = top + random.randint(5,50)
        color = randomColor()
        data.rects.append((left, top, right, bottom, color))
    data.ovalX = 200
    data.timerDelay = 1

def mousePressed(event, data): pass
def keyPressed(event, data): pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def deltaDrawWrapper(canvas, data):
        if (data.readyForDeltaDraw == True):
            deltaDraw(canvas, data)
            canvas.update()
        else:
            redrawAllWrapper(canvas, data)

    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    
        data.readyForDeltaDraw = True

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        # redrawAllWrapper(canvas, data)
        deltaDrawWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    data.readyForDeltaDraw = False

    # create the root and the canvas (Note Change: do this BEFORE calling init!)
    root = Tk()
    #root.attributes('-fullscreen', True)

    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(500, 500)