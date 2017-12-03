#author: Lavender Jiang
#contact: yaoj@andrew.cmu.edu
#15112F17 Term Project

################################################################################
############################### Imports ########################################
################################################################################
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
    def __init__(self,x,y,mode,display="button"):
        xs = 40
        yxRatio = 4
        ys = xs/yxRatio
        
        self.cx = x
        self.cy = y
        self.text = display
        self.minx = x - xs
        self.miny = y - ys
        self.maxx = x + xs
        self.maxy = y + ys
        self.mode = mode

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

def bindButton(button,data,canvas):
    button.draw(canvas)
    button.onclick(data)

def convertToInc(stren):
    standard = {"low":5,"medium":10,"high":15,"crazy":20}
    if stren < 30: key = "low"
    elif stren < 50: key = "medium"
    elif stren < 60: key = "high"
    else: key = "crazy"
    return standard[key] 

def testConvertToInc():
    assert(convertToInc(40)==10)
    assert(convertToInc(65)==20)
    print("passed!")

def calcRingInfo(data):
    '''
    Calculate the radius, pattern and color of the ring of current analysis cycle.

    Note:
        Radius are incremented sequentially.
    '''
    print("freqs",data.anaCycle.freq)
    print("pitches",data.anaCycle.pitch)
    print("***********************")
    timeSpan, freq, stren = data.curTime, data.freq, avg(data.anaCycle.stren)
    incR = convertToArea(stren)
    print("data.radii",data.radii)
    if data.ringCount == 1:
        data.firstCircle = incR
        data.lastRadius = incR
    else:
        newR = data.lastRadius+incR
        data.radii.append(newR)
        data.lastRadius = newR

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
############################### Tk Func ########################################
################################################################################

def init(data):
    data.curTime = 0
    data.ringCount = 0
    data.mode = "home"
    data.mouseX = 0
    data.mouseY = 0
    data.freq = 0
    data.pitch = 0
    data.stren = 0
    data.pOffset = 157
    fig = plt.figure()
    ax = plt.subplot()
    x_fft = np.linspace(0,RATE,CHUNK)
    line_fft, = ax.plot(x_fft, np.random.rand(CHUNK), '-', lw=2)
    data.line_fft = line_fft
    ####################only for createMode###########
    data.radii=[]
    data.firstCircle = False
    data.lastRadius = 0
    data.colors = []

    data.rings=[]

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
    bindButton(create_button,data,canvas)
    about_button = button(data.width/2,data.height*2/3 - gap,"help","About")
    bindButton(about_button,data,canvas)
    analysis_button = button(data.width/2,data.height*2/3,"analysis","Analysis")
    bindButton(analysis_button,data,canvas)
    
    #b3 = button(data.width/2,data.height*2/3 - gap*2)
    logo = Image.open('logo.png')
    #canvas.create_image(data.width/2,data.height/2, image=logo)

###############################################################################
############################### Create Mode ####################################
################################################################################
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

    if data.curTime == 1:
        wave1 = wavyRing(canvas,data.width/2,data.height/2,100,130,["blue","blue",0,"yellow"])
        wave2 = wavyRing(canvas,data.width/2,data.height/2,80,100,["red","red",0,"black"])
        data.rings.append(wave1)
        data.rings.append(wave2)

    for ring in data.rings:
        ring.angle += math.pi/6

    #do not draw ring for backgrond noise
    updateAnaCycle(data)
    if data.curTime%5 == 4:
        info = data.anaCycle
        avgStren = avg(info.stren)
        if avgStren > InputThreshold:
            data.ringCount += 1
            calcRingInfo(data)
    
    data.curTime += 1 

def rgbToHex(rgb):
    '''
    @param rgb: a tuple in the form (r,g,b)
    @return: equivalent hex string
    '''
    res="#"
    for val in rgb:
        hexString = hex(val)
        temp = hexString[2:]
        if len(temp)==1:
            temp = "0" + temp
        res += temp
    return res

def testRgbToHex():
    print(rgbToHex((255,0,0)))
    print(rgbToHex((255,3,19)))

def halfStepsBetween(a,b):
    '''Return the number of halfSteps between Two Notes'''
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#","A", "A#", "B"]
    halfStepsA = notes.index(a[:-1]) + (12* (int(a[-1])-1) )
    halfStepsB = notes.index(b[:-1]) + (12* (int(b[-1])-1) )
    return halfStepsA-halfStepsB

def testHalfStepsBetween():
    assert(halfStepsBetween("F1","C1") == 5)
    assert(halfStepsBetween("G4","C1") == 43)
    assert(halfStepsBetween("G4","F#4") == 1)
    assert(halfStepsBetween("F#4","G4") == -1)

def changesInHalfStepsToIntensity(n):
    pass


def freqToColour(f):
    '''
    @param f: frequency of soundwave in Hz
    @var wl: wavelength of light wave in nm
    @return: rgb of the corresponding color

    Note:
        1) Method for mapping soundwave to light wave taken from Flutopedia.
           Link: http://www.flutopedia.com/sound_color.htm
        2) Algorithm for converting wavelength to color comes from StackOverflow User Tarc.
           Link: https://stackoverflow.com/questions/1472514/convert-light-frequency-to-rgb
        3) Frequency below 262Hz (Middle C) is mapped to black.
    '''
    scale = 2**40
    #special case
    if f < 262: return (0, 0, 0)
    if f < 350: scale = 2**41

    # wavelength = speedOfLight / frequency
    f = f * scale
    c = 3 * (10**8)
    wl = int(c / f * 10**9)
    
    #violet
    if wl >= 380 and wl < 440:
        r = abs(wl - 440.) / (440. - 350.)
        g = 0.0
        b = 1.0
   
    #blue
    elif wl >= 440 and wl < 490:
        r = 0.0
        g = (wl - 440.) / (490. - 440.)
        b = 1.0
    
    # bluish green
    elif wl >= 490 and wl < 510:
        r = 0.0
        g = 1.0
        b = abs(wl - 510.) / (510. - 490.)

    #redish green
    elif wl >= 510 and wl < 580:
        r = (wl - 510.) / (580. - 510.)
        g = 1.0
        b = 0.0
    
    #orange
    elif wl >= 580 and wl < 645:
        r = 1.0
        g = abs(wl - 645.) / (645. - 580.)
        b = 0.0

    #red
    elif wl >= 645 and wl <= 780:
        r = 1.0
        g = 0.0
        b = 0.0
    
    #black
    else:
        r = 0.0
        g = 0.0
        b = 0.0

    # intensity correction
    # really violet
    if wl >= 380 and wl < 420: 
        factor = 0.3 + 0.7*(wl - 350) / (420 - 350)
    # regular blue to red
    elif wl >= 420 and wl <= 700:
        factor = 1.0
    #really red
    elif wl > 700 and wl <= 780:
        factor = 0.3 + 0.7*(780 - wl) / (780 - 700)
    else:
        factor = 0.0
    factor *= 255

    return ( int(factor*r), int(factor*g), int(factor*b) )

def testFreqToColor():
    assert(freqToColour(440)==(255, 98, 0)) #A4 --> orange
    assert(freqToColour(666)==(78, 0, 226)) #E5 --> purple
    assert(freqToColour(340)==(89, 0, 206)) #F4 --> different shade of purple

def cyclePitchAnalysis(notes):
    '''
    Determine the color from the overall pitch and density from changes in notes.

    @param pitches: five notes in the analysis cycle, written in English notation
    @return: color in hex and density 
    '''

    pass

def solveAngle(a,b,c):
    '''return the radian angle C corresponding the triangle sidelength c'''
    #c**2 = a**2 + b**2 - 2*a*b*cos(C)
    cosC = ( c**2 - b**2 - a**2 ) / (-2*a*b)
    angle = math.acos(cosC)
    return angle

def solveLength(a,b,C):
    cSqaure = a**2 + b**2 - 2*a*b*math.cos(C)
    return math.sqrt(cSqaure)

def testSolveLength():
    print( solveLength(10,10,degreeToRadian(23)) )

def degreeToRadian(angle):
    return angle/360 * (2*math.pi)

def radianToDegree(angle):
    return roundHalfUp( 360*angle/(2*math.pi) )

def testSolveAngle():  
    assert(solveAngle(3,4,5)==math.pi/2)
    assert(radianToDegree(solveAngle(1,1,1))==60)
    assert(radianToDegree(solveAngle(math.sqrt(3),2,1))==30)
    print("passed!")

def polarToCartesian(r,angle):
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    return x,y

def drawCircleRing(canvas,zeroX,zeroY,innerR,outerR,color,bgColor="black",spacing=0):
    '''

    Given the innerR and outerR of a ring, draw a ring made of circles on Canvas.

    @param zeroX, zeroY: cartesian coordinate of the center of the ring
    @param innerR: the radius of the inner circle which all ring circles are tangent to
    @param outerR: the radius of the outer circle which all ring circles are tangent to
    @param midR: the radius of the midCircle. The centers of all the ring circles is a subset of this circle.
    @param spacing: an integer between 0 and 1 that determines how spreaded-out the circles are.
                    When set to one, each circle are at least their diamater apart.  

    Note:
        All angles used are in radians.
    '''
    r = (outerR - innerR) / 2
    midR = (outerR + innerR) / 2
    halfAngle = solveAngle(midR,midR,r)
    fullAngle = 2 * halfAngle
    angleWithSpace = fullAngle + spacing * fullAngle


    totalCircle = int( (2*math.pi) // angleWithSpace)
    totalFillAngle = (2*math.pi) - totalCircle * angleWithSpace

    #totalCircle = int( (2*math.pi - spacing*fullAngle*totalCircle) // fullAngle)
    unitFillAngle = totalFillAngle/totalCircle 

    
    canvas.create_oval(zeroX-outerR,zeroY-outerR,zeroX+outerR,zeroY+outerR,fill=bgColor)
    startAngle = 0
    for i in range(totalCircle):
        angle = startAngle + i * (unitFillAngle + angleWithSpace)
        cx,cy = polarToCartesian(midR,angle)
        #coordinate offset for different center
        cx += zeroX
        cy += zeroY
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=color)

def drawCircleRingOfCircles(canvas,zeroX,zeroY,innerR,outerR,colours,startAngle=0,spacing=0.7):
    innerColor, midColor, outerColor, bgColor = colours[0],colours[1],colours[2],colours[3]
    r = (outerR - innerR) / 2
    midR = (outerR + innerR) / 2
    halfAngle = solveAngle(midR,midR,r)
    fullAngle = 2 * halfAngle
    angleWithSpace = fullAngle + spacing * fullAngle
    print("angle",angleWithSpace)
    print((2*math.pi) // angleWithSpace)

    #totalFillAngle = 2*math.pi % fullAngle
    totalCircle = int( (2*math.pi) // angleWithSpace)
    totalFillAngle = (2*math.pi) - totalCircle * angleWithSpace

    #totalCircle = int( (2*math.pi - spacing*fullAngle*totalCircle) // fullAngle)
    unitFillAngle = totalFillAngle/totalCircle 

    #startAngle = 0

    overlap = 0.5
    dressingR = solveLength(midR, midR, unitFillAngle + angleWithSpace)/2
    dressingR = dressingR * (1+overlap)
    toppingRatio = 0.8
    toppingR = dressingR * toppingRatio
    toppingColor = "orange"

    for i in range(totalCircle):
        angle = startAngle + i * (unitFillAngle + angleWithSpace)
        cx,cy = polarToCartesian(midR,angle)
        cx += zeroX
        cy += zeroY
        #coordinate offset for different center

        #dressingR = solveLength(midR, midR, unitFillAngle + angleWithSpace)

        #dR = solveLength(midR, midR, spacing * fullAngle + unitFillAngle)
        #print("newR",dressingR)
        #if i <1:
            #print("center",cx,cy)
            #print("fillAngle",radianToDegree(unitFillAngle + angleWithSpace))
        canvas.create_oval(cx-dressingR,cy-dressingR, dressingR+cx,dressingR+cy,fill=bgColor)
        canvas.create_oval(cx-toppingR,cy-toppingR, toppingR+cx,toppingR+cy,fill=toppingColor)

        drawCircleRing(canvas,cx,cy,r/3,r,innerColor)




class wavyRing(object):
    def __init__(self,canvas,zeroX,zeroY,innerR,outerR,colors,startAngle=0):
        self.canvas = canvas
        self.zeroX = zeroX
        self.zeroY = zeroY
        self.innerR = innerR
        self.outerR = outerR
        self.unitR = (outerR - innerR)/4
        self.colors = colors
        self.angle = startAngle

    def draw(self):
        drawCircleRingOfCircles(self.canvas,self.zeroX,self.zeroY,
                                self.innerR,self.innerR + 2*self.unitR,
                                self.colors,self.angle)



class colorfulBeads(object):
    '''
    Has most pitch changes in an analysis cycle
    '''
    def __init__(self,canvas,zeroX,zeroY,innerR,outerR):
        self.canvas = canvas
        self.zeroX = zeroX
        self.zeroY = zeroY
        self.innerR = innerR
        self.outerR = outerR

    def draw(self):
        drawCircleRingOfCircles(self.canvas,self.zeroX,self.zeroY,self.innerR,self.outerR)


class pureRing(object): pass




def createRedrawAll(canvas,data):
    # draw in canvas
    
    
    #drawCircleRingOfCircles(canvas,data.width/2,data.height/2,80,100,["red","red",0,"black"])
    #drawCircleRing(canvas,data.width/2,data.height/2,70,80,"blue")
    #wave1.angle += math.pi/2
    #print(wave1.angle,"DEGREE")
    for ring in data.rings:
        ring.draw()
    #drawCircleRing(canvas,data.width/2,data.height/2,30,70,"violet")
    #drawCircleRing(canvas,data.width/2,data.height/2,30,70,"yellow")
    #drawCircleRing(canvas,data.width/2,data.height/2,10,30,"green")
    return 
    x = data.width/2
    y = data.height/2
    if data.firstCircle == False: return
    innerR = data.firstCircle
    canvas.create_oval(x-innerR,y-innerR,x+innerR,y+innerR,fill="black")
    for r in data.radii:
        canvas.create_oval(x-r,y-r,x+r,y+r,fill=None,width = 2)

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

def run(width=1000, height=800):
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
    init(data)


    p = pyaudio.PyAudio()

    data.stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Pyaudio recording")
    # create the root and the canvas
    root = Tk()
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

#run()