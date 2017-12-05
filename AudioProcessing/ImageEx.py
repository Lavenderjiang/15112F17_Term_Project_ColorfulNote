# imagesDemo1.py
# view in canvas
# read from file
# with transparent pixels
# get size, resize (zoom and subsample)

# image resized, made transparent with:
# http://www.online-image-editor.com/

from tkinter import *

####################################
# customize these functions
####################################

def redrawAll(canvas, data):
    # Draw a background rectangle to highlight the transparency
    # of the images
    canvas.create_rectangle(0, 10, data.width, 190, fill="cyan")
    # Draw the demo info
    font = ("Arial", 16, "bold")
    msg = "Image Demo #1 (read from file)"
    canvas.create_text(data.width/2, 25, text=msg, font=font)
    # Draw the original size image on the left
    imageSize = ( (data.image.width(), data.image.height()) )
    msg = "Full-size " + str(imageSize)
    canvas.create_text(data.width/5, 50, text=msg, font=font)
    canvas.create_image(data.width/5, 100, anchor=N, image=data.image)
    # Draw a half-size image in the middle
    imageSize = ( (data.halfImage.width(), data.halfImage.height()) )
    msg = "Half-size " + str(imageSize)
    canvas.create_text(data.width/2, 50, text=msg, font=font)
    canvas.create_image(data.width/2, 100, anchor=N, image=data.halfImage)
    # Draw a double-size image on the right
    imageSize = ( (data.doubleImage.width(), data.doubleImage.height()) )
    msg = "Double-size " + str(imageSize)
    canvas.create_text(data.width*4/5, 50, text=msg, font=font)
    canvas.create_image(data.width*4/5, 100, anchor=N, image=data.doubleImage)

def init(data):
    data.image = PhotoImage(file="logo.gif")
    data.halfImage = data.image.subsample(2,2)
    data.doubleImage = data.image.zoom(2,2)

def mousePressed(event, data): pass
def keyPressed(event, data): pass
def timerFired(data): pass

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

run(1000, 500)