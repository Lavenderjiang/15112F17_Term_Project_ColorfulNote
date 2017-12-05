# button-demo1.py
# Simple buttons
# approach #1: with global canvas
# approach #2: with local function and closure

from tkinter import *

def button1Pressed():
    # accesses canvas as a global variable
    global canvas # declare global both here and in run()
    canvas.data["count1"] += 1
    redrawAll(canvas)

def button2Pressed(canvas):
    # accesses canvas as a parameter (see local function below)
    # this approach does not use global variables
    canvas.data["count2"] += 1
    redrawAll(canvas)
    
def redrawAll(canvas):
    canvas.delete(ALL)
    # background (fill canvas)
    canvas.create_rectangle(0,0,300,300,fill="cyan")
    # print counts
    msg = "count1: " + str(canvas.data["count1"])
    canvas.create_text(150,130,text=msg)
    msg = "count2: " + str(canvas.data["count2"])
    canvas.create_text(150,170,text=msg)

def init(root, canvas):
    canvas.data["count1"] = 0
    canvas.data["count2"] = 0
    b1 = Button(root, text="button1", command=button1Pressed)
    b1.pack()
    # Here is the local function and "canvas" is in the closure
    def b2Pressed(): button2Pressed(canvas)
    b2 = Button(root, text="button2", command=b2Pressed)
    b2.pack()
    redrawAll(canvas)

########### copy-paste below here ###########

def run():
    # create the root and the canvas
    root = Tk()
    global canvas # make canvas global for button1Pressed function
    canvas = Canvas(root, width=300, height=300)
    canvas.pack()
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call init
    canvas.data = { }
    init(root, canvas)
    # set up events
    #root.bind("<Button-1>", mousePressed)
    #root.bind("<Key>", keyPressed)
    #timerFired(canvas)
    # and launch the app
    root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)

run()