# events-example0.py
# Barebones timer, mouse, and keyboard events
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
import decimal
from random import uniform #generate random float
from random import randint
from ast import literal_eval

fft = np.fft.fft
np.set_printoptions(threshold=np.nan) #print full np array

####################################
# customize these functions
####################################
CHUNK =  1024*2
FORMAT = pyaudio.paInt16
CHANNELS = 1 #built-in microphone is monotone
RATE = 16000

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
    threshold = 5
    #sound with volume below threshold is considered noise 
    if stren<threshold: return 5
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
    #print(arrayGen(0,800,1024))
    print(arrayGen(0,800,2048))

def rawAnalysis(data,rawData):
    rawData_int = struct.unpack(str(2*CHUNK)+'B',rawData)
    y_fft = fft(rawData_int)
        #slice to get ride of conjugate and rescale
    y_scaled = np.abs(y_fft[:CHUNK]) * 2 / (128*CHUNK)
    y_final = y_scaled[20:]
    #print(y_final)
    #print("lenYFINAL",len(y_final))
    #print("TYPEy",type(y_final))
    #print(y_final)
    maxAmp = max(y_final)
    maxIndex = np.where(y_final==maxAmp)
    print(maxIndex)
    #x_fft
    #freqs = np.arange(0, 2 * CHUNK, 2)
    line_fft = data.line_fft
    freqs =line_fft.get_xdata()
    print("lenFreqs",len(freqs))
    #print(freqs)

    curFreq = freqs[maxIndex] + data.pOffset
    print("curF",curFreq)
    curPitch = fToNote(curFreq)

    y_pureAmplitude = np.array(rawData_int, dtype='b')[::2] 
    avgAmp = np.asscalar(sum(np.abs(y_pureAmplitude))/len(y_pureAmplitude))
    print("f",curFreq,"P",curPitch,"A",avgAmp)
    return curFreq,curPitch,avgAmp

def freqToCanvasY(totalY,f):
    f=f[0]
    unit = totalY/800
    return totalY-unit*f

def testFreqToY():
    print(freqToCanvasY(400,600)) #100
    print(freqToCanvasY(400,400)) #200
    print(freqToCanvasY(400,700)) #50

################################################################################
############################### Tk Func ########################################
################################################################################

def init(data):
    # load data.xyz as appropriate
    data.mode = "home"
    data.freq = 0
    data.pitch = 0
    data.stren = 0
    data.pOffset = 157
    fig = plt.figure()
    ax = plt.subplot()
    x_fft = np.linspace(0,RATE,CHUNK)
    line_fft, = ax.plot(x_fft, np.random.rand(CHUNK), '-', lw=2)
    data.line_fft = line_fft

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    if data.mode == "home": homeTimerFired(data)
    if data.mode == "analysis": analysisTimerFired(data)


def analysisTimerFired(data):
    stream = data.stream
    rawData = stream.read(CHUNK,exception_on_overflow = False)
    data.freq,data.pitch,data.stren=rawAnalysis(data,rawData)


def homeTimerFired(data):
    pass

def redrawAll(canvas,data):
    if data.mode == "home": homeRedrawAll(canvas,data)
    if data.mode == "analysis": analysisRedrawAll(canvas,data)

def analysisRedrawAll(canvas, data):
    # draw in canvas
    x = data.width/2
    y = freqToCanvasY(data.height,data.freq)
    print("y",y)
    r = convertToArea(data.stren)
    canvas.create_oval(x-r,y-r,x+r,y+r, fill="purple", width=0)

def homeRedrawAll(canvas,data):
    canvas.create_rectangle(0,0,data.width,data.height,fill="#FFEE93",width=0)
    logo = PhotoImage(file='pic/logo.png')
    canvas.create_image(data.width/2, data.height/2, image=logo)

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

#run(600, 600)