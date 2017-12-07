#author: Lavender Jiang
#contact: yaoj@andrew.cmu.edu
#15112F17 Term Project

################################################################################
############################### Imports ########################################
################################################################################
from drawHelper import *
from musicHelper import *
import pyaudio
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from tkinter import *
from GUIclasses import *
import struct
import numpy as np
from math import log2
import math
import decimal
from random import uniform #generate random float
from random import randint
from ast import literal_eval
from PIL import Image
from PIL import ImageGrab
from tkinter import filedialog
import webbrowser
import os

fft = np.fft.fft
np.set_printoptions(threshold=np.nan) #print full np array


################################################################################
############################### Globals ########################################
################################################################################

CHUNK =  1024*2
FORMAT = pyaudio.paInt16
CHANNELS = 1 #built-in microphone is monotone
RATE = 16000

InputThreshold = 6

################################################################################
############################### Helpers ########################################
################################################################################
            
#copied from 112 course website
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def debugPrint(data):
    ringList = data.rings
    for ring in ringList:
        if type(ring)==firstCircle: continue
        print(ring.innerR,ring.outerR,type(ring).__name__)

def avg(l):
    return sum(l)/len(l)

def fToNote(f):
    '''
    f Range: A0(27.5Hz) ~ G5(783Hz)
    @param f: frequency in range
    @return: a string of English notation of musical notes (e.g. A4)
    '''
    #f = np.asscalar(f) #convert to scalar
    C0 = 16.35
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    halfSteps = roundHalfUp(12*log2(f/C0)) #formula taken from John D. Cook
    octave = abs(halfSteps/12)
    pitch = notes[halfSteps%12]
    return "%s%d"%(pitch,octave)

def testFConversion():
    print(fToNote(440)) #A4
    print(fToNote(391)) #G4
    print(fToNote(800)) #G5
    print(fToNote(743)) #Fsharp5

def fToAngle(f):
    '''
    f Range: A0(27.5Hz) ~ G5(783Hz)
    @param f: frequency in range
    @return: the polar angle of a circle in radians
    '''
    unitAngle = 2*np.pi/59
    C0 = 16.35
    halfStepsToC0 = roundHalfUp(12*log2(f/C0))
    halfStepsToA0 = halfStepsToC0 - 9
    startAngle = unitAngle * halfStepsToA0
    fAngle = uniform(startAngle,startAngle+unitAngle)
    return fAngle

def testAngleConversion():
    fToAngle(800) #around 360 degree
    fToAngle(27.5) #around 0 degree
    fToAngle(400) #around 300 degree

def convertToArea(stren):
    '''
    stren Range: 0 ~ 70
    @param stren: volume/amplitude of current sample
    @return: the area of a circle
    '''
    
    #sound with volume below threshold is considered noise 
    if stren<InputThreshold: return None
    #generate random value in specified range
    elif stren<30: res = stren*0.8
    elif stren<50: res = stren
    elif stren<60: res = stren*1.2
    else: res = stren*1.2
    return res

def testAreaConversion():
    print(convertToArea(42.7)) #('low',5)
    print(convertToArea(68.9)) #('high', 20)
    
def extractData():
    '''Write frequency and strength data to .txt file.'''
    f = open("data.txt","r")
    res = []
    #use literal_eval to safety turn string back to tuple
    for line in f:
        res.append(literal_eval(line))
    #first is frequency(0~800), second is strength(0~70)
    for d in res:
        freq = d[0]
        pitch = fToNote(freq)
        stren = d[1]

def calcDotRing(r,a):
    '''
    @param r: curR calculated from time
    @param a: curA calculated from sound stren
    @return: param to append for a ring of colored circles
    '''
    angles = np.arange(2*np.pi,step=0.05)
    radii = [r for i in range(len(angles))]
    areas = [a for i in range(len(angles))]
    return angles,radii,areas

def testCalcRing():
    print(calcDotRing(3,20))
    print(calcDotRing(5,30))

def arrayGen(start,stop,steps):
    unitLen = (stop - start)/steps
    res = [start + i * unitLen for i in range(steps)]
    return res

def testArrayGen():
    print(arrayGen(0,800,1024))
    print(arrayGen(0,800,2048))

def rawAnalysis(data,rawData):
    rawData_int = struct.unpack(str(2*CHUNK)+'B',rawData)
    y_fft = fft(rawData_int)
        #slice to get ride of conjugate and rescale
    y_scaled = np.abs(y_fft[:CHUNK]) * 2 / (128*CHUNK)
    y_final = y_scaled[20:]

    maxAmp = max(y_final)
    maxIndex = np.where(y_final==maxAmp)
 
    line_fft = data.line_fft
    freqs =line_fft.get_xdata()

    curFreq = freqs[maxIndex] + data.pOffset
    curFreq = np.asscalar(curFreq)%800 
    curPitch = fToNote(curFreq)

    y_pureAmplitude = np.array(rawData_int, dtype='b')[::2] 
    avgAmp = np.asscalar(sum(np.abs(y_pureAmplitude))/len(y_pureAmplitude))
    #print("f",curFreq,"P",curPitch,"A",avgAmp)
    return curFreq,curPitch,avgAmp

def freqToCanvasY(totalY,f):
    #if isinstance(f,int): pass
    #else: f = np.asscalar(f)
    unit = totalY/800
    return totalY-unit*f

def testFreqToY():
    print(freqToCanvasY(400,600)) #100
    print(freqToCanvasY(400,400)) #200
    print(freqToCanvasY(400,700)) #50


def cyclePitchAnalysis(data):
    '''
    Determine the color from the overall pitch and density from changes in notes.

    @param pitches: five notes in the analysis cycle, written in English notation
    @return: ringType, a list of color, and inner&outer radius
    '''
    
    if len(data.rings) == 0:
        data.ringType = "pure" #one color
    else:
        #update data.ringType and data.diffList
        NoteListToType(data.anaCycle.pitch,data)
    #update data.incR
    strenToIncR(avg(data.anaCycle.stren),data)
    #update data.colors
    colorListGen(data)
    #notify redrawAll
    data.addFlag = True

def updateAnaCycle(data):
    '''
    Update the audio info in one analysis cycle.
    @param anaCycle: the struct that contains all audio info
    '''
    if data.curTime %5 == 0:
        data.anaCycle.stren = [data.stren]
        data.anaCycle.freq = [data.freq]
        data.anaCycle.pitch = [data.pitch]
    else:
        data.anaCycle.stren.append(data.stren)
        data.anaCycle.freq.append(data.freq)
        data.anaCycle.pitch.append(data.pitch) 

################################################################################
############################### Tk Func ########################################
################################################################################
def init(data):

    data.curTime = 0
    data.ringCount = 0
    data.radii=[]
    data.firstCircle = False
    data.oldR = 0
    data.colors = []
    data.rings=[]
    data.ringType=""
    data.incR=0

    
    data.diffList=[]
    class Struct(object): pass
    data.anaCycle = Struct()
    data.freq = 0
    data.pitch = 0
    data.stren = 0
    data.pOffset = 157

    ########## matplotlib data ######## 
    fig = plt.figure()
    ax = plt.subplot()
    x_fft = np.linspace(0,RATE,CHUNK)
    line_fft, = ax.plot(x_fft, np.random.rand(CHUNK), '-', lw=2)
    data.line_fft = line_fft
    ####################only for createMode###########
    

    data.bgColor="black"

    data.logo = PhotoImage(file="logo.gif")
    data.ex1 = PhotoImage(file="imagine.gif")
    data.ex2 = PhotoImage(file="libertango.gif")

    dancingNoteInit(data)
    menuInit(data)

    data.homeButton = button(data.width/4,data.height/4,"home","home")
    data.saveButton = saveButton(data.width/4,data.height/5,"save","save")
    
    #status init
    data.mode = "home"
    data.saved = False
    data.shared = False
    data.stop = False
    data.fullFlag = False
    data.addFlag=False
    data.mouseX = 0
    data.mouseY = 0

    data.items = []


def mousePressed(event, data):
    # use event.x and event.y
    if data.mode == "home": homeMousePressed(event,data)
    if data.mode == "analysis": analysisMousePressed(event,data)
    if data.mode == "help": helpMousePressed(event,data)
    if data.mode == "create": createMousePressed(event,data)

def keyPressed(event, data):
    # use event.char and event.keysym
    if data.mode == "home": homeKeyPressed(event,data)
    if data.mode == "create": createKeyPressed(event,data)
    if data.mode == "analysis": analysisKeyPressed(event,data)

def timerFired(canvas,data):
    if data.mode == "home": homeTimerFired(data)
    if data.mode == "analysis": analysisTimerFired(data)
    if data.mode == "create": createTimerFired(canvas,data)

def deltaDraw(canvas,data):
    if data.mode == "home": homeDeltaDraw(canvas,data)
    if data.mode == "create": createDeltaDraw(canvas,data)
    if data.mode == "analysis": analysisDeltaDraw(canvas,data)
    if data.mode == "help": helpDeltaDraw(canvas,data)


def redrawAll(canvas,data):
    if data.mode == "home": homeRedrawAll(canvas,data)
    if data.mode == "create": createRedrawAll(canvas,data)
    if data.mode == "analysis": analysisRedrawAll(canvas,data)
    if data.mode == "help": helpRedrawAll(canvas,data)


################################################################################
############################### Home Mode ######################################
################################################################################

def homeTimerFired(data):
    pass

def homeMousePressed(event,data):
    data.mouseX = event.x
    data.mouseY = event.y


def homeKeyPressed(event, data):
    pass

def homeDeltaDraw(canvas, data):
    pass

def homeRedrawAll(canvas,data):
    #filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    
    canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)
    gap = 30
    create_button = button(data.width/2,data.height*2/3 - 2*gap,"create","Create!")
    bindButton(create_button,data)
    about_button = button(data.width/2,data.height*2/3 - gap,"help","About")
    bindButton(about_button,data)
    analysis_button = button(data.width/2,data.height*2/3,"analysis","Analysis")
    bindButton(analysis_button,data)
    canvas.create_image(data.width/2, data.height/3,  image=data.logo)
    data.readyForDeltaDraw = True
    

###############################################################################
############################### Create Mode ####################################
################################################################################


def createTimerFired(canvas,data):
    '''
    Update the drawing data for ring geometric art. In each analysis cycle, one
    ring is drawn. Its spacing with the previous ring is decided by its stren. 

    @var curTime: keep time with unit time 0.1 second
    @var curCycle: the current analysis cycle (each cycle is 0.5 second)

    Note:
        For cycle with low stren, no ring is drawn. 
    '''
    
    #Receive and analyse audio data
    if data.stop == False:

        stream = data.stream
        rawData = stream.read(CHUNK,exception_on_overflow = False)
        data.freq, data.pitch, data.stren = rawAnalysis(data,rawData)        

        if data.stren > InputThreshold:
            data.dance = True
        else:
            data.dance = False
        #for ring in data.rings:
            #ring.angle += math.pi/6

        #do not draw ring for backgrond noise
        updateAnaCycle(data)
        if data.curTime%5 == 4:
            #print(data.anaCycle.stren)
            avgStren = avg(data.anaCycle.stren)
            #print("avg!!!",avgStren)
            if avgStren > InputThreshold:
                cyclePitchAnalysis(data)
                #debugPrint(data)

        verticalJump(data)
        
        data.curTime += 1 

def createDeltaDraw(canvas, data):
 
    canvas.coords(data.dancingNote,(data.width/12,data.dancingHeight))

    if data.addFlag == True and data.stop==False:
        offsetX, offsetY = data.width/6-100, 0
        zeroX,zeroY = data.width/2 + offsetX, data.height/2 + offsetY
        innerR = data.oldR
        outerR = data.oldR + data.incR

        #check if out of bound
        if zeroX + outerR > data.width or zeroX - outerR < data.width/6 or\
           zeroY + outerR > data.height or zeroY - outerR < 0:
           data.fullFlag = True

        if len(data.rings)==0:
            ring = firstCircle(canvas,zeroX,zeroY,data.colors[0],data.incR)
            #data.oldR = data.incR
        elif data.ringType == "pure":
            ring = pureRing(canvas,zeroX,zeroY,innerR,outerR,data.colors)
        elif data.ringType == "bead":
            ring = colorfulBeads(canvas,zeroX,zeroY,innerR,outerR,data.colors)
        elif data.ringType == "wavy":
            ring = wavyRing(canvas,zeroX,zeroY,innerR,outerR,data.colors)        
        data.oldR = data.oldR+data.incR


        data.rings.append(ring)
        ring.draw(data)

        data.addFlag = False

    if data.fullFlag == True:
        data.fullFlag = False
        scale = 0.6
        threshold = 1.5
        data.oldR = data.oldR * scale
        for ring in data.rings:
            if type(ring)==firstCircle: continue
            ring.innerR = ring.innerR * scale
            ring.outerR = ring.outerR * scale
            if ring.outerR < data.rings[0].r * threshold :
                ring.delete = True
        data.readyForDeltaDraw = False

def createRedrawAll(canvas,data):
    data.bgItem = canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)


    #reverse to avoid hiding of the previous rings
    for ring in data.rings[::-1]:
        ring.draw(data)

    canvas.create_rectangle(0,0,data.width/6,data.height,fill="#44d9e6",width=3)
    
    data.createMenu.drawMenu()
    texts = ["Sing something to begin :)",
             "Press ↑ to zoom in!",
             "Press ↓ to zoon out!",
             "Press w,a,s,d to move!"]
    textRow(canvas,0,data.width/6,2*data.height/3-40,data.height-150,
            texts)

    canvas.create_rectangle(0,data.height-150,data.width/6,data.height,fill="#44d9e6",width=3)

    data.dancingNote = canvas.create_image(data.width/12, data.dancingHeight, image=data.note)

    data.readyForDeltaDraw = True

def createMousePressed(event,data):
    data.mouseX = event.x
    data.mouseY = event.y

def createKeyPressed(event,data):
    if event.keysym == "Up":
        scale = 1.1
        for ring in data.rings:
            if type(ring)==firstCircle: continue
            ring.innerR = ring.innerR * scale
            ring.outerR = ring.outerR * scale
            if ring.innerR > data.width:
                ring.delete = True
        data.readyForDeltaDraw = False

    if event.keysym == "Down":
        scale = 0.9
        for ring in data.rings:
            if type(ring)==firstCircle: continue
            ring.innerR = ring.innerR * scale
            ring.outerR = ring.outerR * scale
            if ring.innerR < data.rings[0].r:
                ring.delete = True
        data.readyForDeltaDraw = False

    if event.keysym == "w":
        step = -20
        for ring in data.rings:
            ring.zeroY += step
        data.readyForDeltaDraw = False

    if event.keysym == "s":
        step = 20
        for ring in data.rings:
            ring.zeroY += step
        data.readyForDeltaDraw = False

    if event.keysym == "a":
        step = -20
        for ring in data.rings:
            ring.zeroX += step
        data.readyForDeltaDraw = False
        
    if event.keysym == "d":
        step = 20
        for ring in data.rings:
            ring.zeroX += step
        data.readyForDeltaDraw = False

################################################################################
############################### Help Mode ######################################
################################################################################

def helpMousePressed(event,data):
    data.mouseX = event.x
    data.mouseY = event.y

def helpRedrawAll(canvas,data):
    offset = 30
    canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)
    canvas.create_image(offset,offset,image=data.ex1)
    canvas.create_image(data.width-offset,data.height-offset,image=data.ex2)

    left = data.width/5
    top = data.height/5 
    right = data.width -left
    down = data.height - top
    canvas.create_rectangle(left,top,right,down,fill="#44d9e6",width=3)
    texts = ["ColorfulNote turn your music into art!",
             "The image on top left corner is Lennon's IMAGINE",
             "The image on bottom right corner is LIBERTANGO",
             "Now you see the music :)",
             "To start painting with song,",
             "Go to CREATE mode!",
             "If you wonder how ColorfulNote works",
             "Go to ANALYSIS mode!",
             "Have fun!"]
    textRow(canvas,left,right,top+50,down,texts,"#d64a9c")
    #canvas.create_text(data.width/2,data.height/2,text="HELP!!!!")
    data.readyForDeltaDraw = True
    #b1 = button(data.width/4,data.height/4,"home","home")
    

def helpDeltaDraw(canvas, data):
    bindButton(data.homeButton,data)

################################################################################
############################# Analysis Mode ####################################
################################################################################

def analysisTimerFired(data):
    stream = data.stream
    rawData = stream.read(CHUNK,exception_on_overflow = False)
    data.freq,data.pitch,data.stren=rawAnalysis(data,rawData)
    updateAnaCycle(data)
    if data.curTime%5 == 4:
        #print(data.anaCycle.stren)
        avgStren = avg(data.anaCycle.stren)
        #print("avg!!!",avgStren)
        if avgStren > InputThreshold:
            cyclePitchAnalysis(data)
    data.curTime += 1

def drawGrid(canvas,data,x0,y0,x1,y1,rows,cols,color,start=8,end=8):
    #from C4 to G5 
    colors = []
    freqs = [                                    208, 220, 233, 247,
             262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494,
             523, 554, 587, 622, 659, 698, 740, 784, 196]
    for freq in freqs:
        rgb = freqToColour(freq)
        hexColor = rgbToHex(rgb)
        colors.append(hexColor)

    dx = (x1 - x0) / cols
    dy = (y1 - y0) / rows

    count = 0
    lastRow = False

    for r in range(rows):
        print("r",r)
        if r == rows -1: lastRow = True
        curY = y0 + r * dy
        for c in range(cols):
            curX = x0 + c*dx
            if count < start-1 or end < 1:
                color,thickness = None,0 
            else:
                print("colorIndex",r*cols+c-(start-1))
                i = r*cols+c-start
                color = colors[i]
                thickness = 3
                canvas.create_rectangle(curX,curY,curX+dx,curY+dy,fill=color,width=thickness)
                note = fToNote(freqs[i])
                canvas.create_text(curX+dx/2,curY+dy/2,text=note,font="Helvetica 17 bold")
            count += 1
            print("end",end)
            if lastRow: end -= 1

def analysisRedrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)
    drawGrid(canvas,data,data.width/4-40,data.height/3-70,3*data.width/4+40,data.height/1.5-70,3,12,"white")
    #canvas.create_rectangle(0,data.height*(1-1/5),data.width,data.height,fill=None,width=3)
    data.oldX = 0
    data.oldR = 0
    cy = 9/10*data.height
    r = 10
    #data.noteCircle = canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill="black",width=3)
    data.readyForDeltaDraw = True



def deltaDrawCircle(canvas,data):
    #print("delta drawing!")
    tScale = 10
    dx = 10
    basef = 196
    topf = 784
    color = curFreqToHex(data.freq)
    r = convertToArea(data.stren)
    if r != None:
        cx = data.oldX + data.oldR + r
        cy = data.height - (data.freq % basef) * (data.height-data.height/5)/(topf-basef)
        #cx = data.curTime * tScale % data.width
        #cy = 9/10*data.height
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=color,width=3)
        data.oldX, data.oldR = cx, r
        if cx+r >= data.width:
            print("overflow!")
            canvas.create_rectangle(0,data.height*(1-1/3)-50,data.width,data.height,fill="#FFEE93",width=0)
            data.oldX = 0


    # canvas.coords(data.noteCircle,(cx-r,cy-r,cx+r,cy+r))
    # canvas.itemconfig(data.noteCircle,fill=color)

def deltaDrawRing(canvas,data):
    if data.addFlag == True:
        print("colors",data.colors)

        zeroX,zeroY = 0,0
        innerR = 200
        outerR = 270
        offset = 10
        canvas.create_oval(zeroX-outerR-offset,zeroY-outerR-offset,
                           zeroX+outerR+offset,zeroY+outerR+offset,
                           fill = "#FFEE93",width=0)

        if data.ringType == "wavy":
            ring = wavyRing(canvas,zeroX,zeroY,innerR,outerR,data.colors)
        elif data.ringType == "pure":
            ring = pureRing(canvas,zeroX,zeroY,innerR,outerR,data.colors)
        elif data.ringType == "bead":
            ring = colorfulBeads(canvas,zeroX,zeroY,innerR,outerR,data.colors)
                
        
        data.ring = ring
        ring.draw(data)

        data.addFlag = False

def analysisDeltaDraw(canvas, data):
    bindButton(data.homeButton,data)
    deltaDrawCircle(canvas,data)
    deltaDrawRing(canvas,data)

def analysisMousePressed(event,data):
    data.mouseX = event.x
    data.mouseY = event.y

def analysisKeyPressed(event,data):
    pass
################################################################################
############################# Main Function ####################################
################################################################################

def run(width=1200, height=700):
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
           

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(canvas, data)
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

    p = pyaudio.PyAudio()

    data.stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Pyaudio recording")
    # create the root and the canvas
    root = Tk()
    data.root=root
    #root.attributes('-fullscreen', True)

    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    data.canvas = canvas

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

run()