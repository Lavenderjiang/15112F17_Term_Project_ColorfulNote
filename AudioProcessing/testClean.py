#author: Lavender Jiang
#contact: yaoj@andrew.cmu.edu
#15112F17 Term Project

################################################################################
############################### Imports ########################################
################################################################################
import drawHelper
import musicHelper
import pyaudio
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from tkinter import *
import struct
import numpy as np
from math import log2
import math
import decimal
from random import uniform #generate random float
from random import randint
from ast import literal_eval
from PIL import Image

fft = np.fft.fft
np.set_printoptions(threshold=np.nan) #print full np array



################################################################################
############################### Globals ########################################
################################################################################

CHUNK =  1024*2
FORMAT = pyaudio.paInt16
CHANNELS = 1 #built-in microphone is monotone
RATE = 16000

InputThreshold = 10

################################################################################
############################### Helpers ########################################
################################################################################
            
#copied from 112 course website
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

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
    octave = halfSteps/12
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
    if stren<InputThreshold: return 5
    #generate random value in specified range
    elif stren<30: res = randint(5,30)
    elif stren<50: res = randint(30,50)
    elif stren<60: res = randint(50,100)
    else: res = randint(100,150)
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
        self.minx = x - xs
        self.miny = y - ys
        self.maxx = x + xs
        self.maxy = y + ys
        
    def draw(self,canvas):
        color = "blue"
        thickness = 2
        canvas.create_rectangle(self.minx,self.miny,self.maxx,self.maxy,
                                fill=color,width=2)
        canvas.create_text(self.cx,self.cy,text=self.text)

    def onclick(self,data):
        #switch mode and reset time
        if data.mouseX > self.minx and data.mouseX < self.maxx \
        and data.mouseY > self.miny and data.mouseY < self.maxy:
            data.mode = self.mode 
            data.curTime = 0 

def bindButton(button,data):
    button.draw(data.canvas)
    button.onclick(data)



# def calcRingInfo(data):
#     '''
#     Calculate the radius, pattern and color of the ring of current analysis cycle.
#     Update the results to data.

#     Note:
#         Radius are incremented sequentially.
#     '''
#     print("freqs",data.anaCycle.freq)
#     print("pitches",data.anaCycle.pitch)
#     print("stren",data.anaCycle.stren)
#     print("***********************")
#     timeSpan, freq, stren = data.curTime, data.freq, avg(data.anaCycle.stren)
#     incR = convertToArea(stren)
#     print("data.radii",data.radii)
#     if data.ringCount == 1:
#         data.firstCircle = incR
#         data.lastRadius = incR
#     else:
#         newR = data.lastRadius+incR
#         data.radii.append(newR)
#         data.lastRadius = newR

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
        #print(data.anaCycle.pitch,data.anaCycle.stren)

################################################################################
############################### Ring Class #####################################
################################################################################
class firstCircle(object):
    def __init__(self,canvas,cx,cy,color,radius):
        self.canvas=canvas
        self.color = color
        self.cx = cx
        self.cy = cy
        self.r = radius
        self.angle = 0

    def draw(self):
        cx = self.cx
        cy = self.cy
        r=self.r
        self.canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=self.color)


class musicRing(object):
    def __init__(self,canvas,zeroX,zeroY,innerR,outerR,colors,startAngle=0):
        self.canvas = canvas
        self.zeroX = zeroX
        self.zeroY = zeroY
        self.innerR = innerR
        self.outerR = outerR
        self.unitR = (outerR - innerR)/4
        self.colors = colors
        self.angle = startAngle

    def scale(self,factor):
        '''change inner and outerR'''
        pass

    def translate(self,coord):
        '''move center'''
        pass

class wavyRing(musicRing):

    def draw(self):
        drawHelper.drawCircleRingOfCircles(self.canvas,self.zeroX,self.zeroY,
                                self.innerR,self.innerR + 2*self.unitR,
                                self.colors,self.angle)

class colorfulBeads(musicRing):
    '''
    Has most pitch changes in an analysis cycle
    '''
    def draw(self):
        drawHelper.drawColorfulBeads(self.canvas,self.zeroX,self.zeroY,
                          self.innerR,self.outerR,self.colors,self.angle)


class pureRing(musicRing):

    def draw(self):
        drawHelper.drawPureRing(self.canvas,self.zeroX,self.zeroY,
                     self.innerR,self.outerR,self.colors,self.angle)

################################################################################
############################### Tk Func ########################################
################################################################################

def init(data):
    data.logo = PhotoImage(file="logo.gif")
    data.curTime = 0
    data.ringCount = 0
    data.mode = "home"
    data.mouseX = 0
    data.mouseY = 0
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
    data.radii=[]
    data.firstCircle = False
    data.oldR = 0
    data.colors = []

    data.rings=[]
    data.ringType=""
    data.incR=0
    data.diffList=[]

    data.addFlag=False
    data.bgColor="black"

    class Struct(object): pass
    data.anaCycle = Struct()

def mousePressed(event, data):
    # use event.x and event.y
    if data.mode == "home": homeMousePressed(event,data)
    if data.mode == "analysis": analysisMousePressed(event,data)
    if data.mode == "help": helpMousePressed(event,data)
    if data.mode == "create": createMousePressed(event,data)

def keyPressed(event, data):
    # use event.char and event.keysym
    if data.mode == "home": homeKeyPressed(event,data)
    if data.mode == "analysis": analysisKeyPressed(event,data)

def timerFired(canvas,data):
    if data.mode == "home": homeTimerFired(data)
    if data.mode == "analysis": analysisTimerFired(data)
    if data.mode == "create": createTimerFired(canvas,data)


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

def homeRedrawAll(canvas,data):
    #print("curXY!",data.mouseX,data.mouseY)
    canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)
    gap = 30
    create_button = button(data.width/2,data.height*2/3 - 2*gap,"create","Create!")
    bindButton(create_button,data)
    about_button = button(data.width/2,data.height*2/3 - gap,"help","About")
    bindButton(about_button,data)
    analysis_button = button(data.width/2,data.height*2/3,"analysis","Analysis")
    bindButton(analysis_button,data)
    
    #b3 = button(data.width/2,data.height*2/3 - gap*2)
    canvas.create_image(data.width/2,data.height/3, image=data.logo)

###############################################################################
############################### Create Mode ####################################
################################################################################
def debugPrint(data):
    ringList = data.rings
    for ring in ringList:
        if type(ring)==firstCircle: continue
        print(ring.innerR,ring.outerR,type(ring).__name__)

def avg(l):
    return sum(l)/len(l)

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
    stream = data.stream
    rawData = stream.read(CHUNK,exception_on_overflow = False)
    data.freq,data.pitch,data.stren=rawAnalysis(data,rawData)        

    for ring in data.rings:
        ring.angle += math.pi/6

    #do not draw ring for backgrond noise
    updateAnaCycle(data)
    if data.curTime%5 == 4:
        #print(data.anaCycle.stren)
        avgStren = avg(data.anaCycle.stren)
        #print("avg!!!",avgStren)
        if avgStren > InputThreshold:
            cyclePitchAnalysis(data)
            #debugPrint(data)
    
    data.curTime += 1 

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
        musicHelper.NoteListToType(data.anaCycle.pitch,data)
    #update data.incR
    musicHelper.strenToIncR(avg(data.anaCycle.stren),data)
    #update data.colors
    musicHelper.colorListGen(data)
    #notify redrawAll
    data.addFlag = True


def createRedrawAll(canvas,data):
    if data.addFlag == True:
        zeroX,zeroY = data.width/2,data.height/2
        innerR = data.oldR
        outerR = data.oldR + data.incR
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
        print("old",data.oldR,"inc",data.incR)
        print("##############################")
        data.rings.append(ring)
        data.addFlag = False

    #reverse to avoid hiding of the previous rings
    for ring in data.rings[::-1]:
        ring.draw()
    #drawCircleRing(canvas,data.width/2,data.height/2,30,70,"violet")
    #drawCircleRing(canvas,data.width/2,data.height/2,30,70,"yellow")
    #drawCircleRing(canvas,data.width/2,data.height/2,10,30,"green")
   


def createMousePressed(event,data):
    pass


################################################################################
############################### Help Mode ######################################
################################################################################


def helpMousePressed(event,data):
    data.mouseX = event.x
    data.mouseY = event.y

def helpRedrawAll(canvas,data):
    canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)
    canvas.create_text(data.width/2,data.height/2,text="HELP!!!!")
    b1 = button(data.width/4,data.height/4,"home")
    bindButton(b1,data,canvas)



################################################################################
############################# Analysis Mode ####################################
################################################################################


def analysisTimerFired(data):
    stream = data.stream
    rawData = stream.read(CHUNK,exception_on_overflow = False)
    data.freq,data.pitch,data.stren=rawAnalysis(data,rawData)
    data.freq = np.asscalar(data.freq)

def analysisRedrawAll(canvas, data):
    # draw in canvas
    x = data.width/2
    y = freqToCanvasY(data.height,data.freq)
    print("y",y)
    r = convertToArea(data.stren)
    canvas.create_oval(x-r,y-r,x+r,y+r, fill="purple", width=0)
    canvas.create_text(data.width*2/3,data.height*3/4,text = fToNote(data.freq))
    canvas.create_text(data.width*2/3,data.height*3/4-20,text = str(data.freq))



################################################################################
############################# Main Function ####################################
################################################################################

def run(width=1200, height=800):
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
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init

    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    
    #init(data)
    



    p = pyaudio.PyAudio()

    data.stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Pyaudio recording")
    # create the root and the canvas
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

run()