# dialogs-demo1.py
# demo standard dialogs
# messagebox: Info box, warning box, error box, and question box
# tkSimpleDialog: Askstring box

from tkinter import *
from tkinter import messagebox, simpledialog

####################################
# customize these functions
####################################

def choose(message, title, options):
    msg = message + "\n" + "Choose one:"
    for i in range(len(options)):
        msg += "\n" + str(i+1) + ": " + options[i]
    response = simpledialog.askstring(title, msg)
    try:
        return options[int(response)-1]
    except:
        return None

def button1Pressed(data):
    # Info Box
    message = "This is a message!  It is only a message!"
    title = "Info box"
    messagebox.showinfo(title, message)
    # Warning Box
    message = "Warning, warning, something might be amiss!"
    title = "Warning box"
    messagebox.showwarning(title, message)
    # Error Box
    message = "Red alert!  Red alert!  Something is definitely wrong!"
    title = "Error box"
    messagebox.showerror(title, message)
    # Question Box
    message = "Would you like to answer 'yes' to this question?"
    title = "Ask Question Box"
    response = messagebox.askquestion(title, message)
    message = "You just answered: " + str(response)
    title = "Response (Info box)"
    messagebox.showinfo(title, message)
    # AskString Box
    message = "What is your favorite color?"
    title = "AskString Box"
    options = [ "red", "green", "blue", "something else" ]
    response = choose(message, title, options)
    message = "You just answered: " + str(response)
    title = "Response (Info box)"
    messagebox.showinfo(title, message)
    # And update and redraw our canvas
    data.message = message
    data.count += 1
    
def redrawAll(canvas, data):
    # background (fill canvas)
    canvas.create_rectangle(0,0,300,300,fill="cyan")
    # print message
    msg = "message: " + str(data.message)
    canvas.create_text(150,130,text=msg)
    msg = "count: " + str(data.count)
    canvas.create_text(150,170,text=msg)

def onButton(data, buttonId):
    if (buttonId == 1): button1Pressed(data)

def init(data):
    data.message = "none"
    data.count = 0
    buttonFrame = Frame(data.root)
    b1 = Button(buttonFrame, text="Click me!", command=lambda:onButton(data,1))
    b1.grid(row=0,column=0)
    buttonFrame.pack(side=TOP)

def mousePressed(event, data): pass
def keyPressed(event, data): pass
def timerFired(event): pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds

    # create the root and the canvas (Note Change: do this BEFORE calling init!)
    root = Tk()

    # Store root in data so buttons can access
    data.root = root

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

run(300, 300)