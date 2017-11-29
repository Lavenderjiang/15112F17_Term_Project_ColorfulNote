#author: Lavender Jiang
#andrewID: yaoj
#15112F17 Term Project

################################################################################
############################### Imports ########################################
################################################################################

'''Dependencies: pyaudio, matplotlib, numpy'''
import pyaudio
from pylab import *
import numpy as np 
import matplotlib as mpl
#mpl.rcParams["backend"] = "Qt4Agg"
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from array import array
import struct
from struct import pack #used to unpack audio data into integer
from ast import literal_eval
from math import log2
import decimal
from random import uniform #generate random float
from random import randint
import wave
np.set_printoptions(threshold=np.nan) #print full np array
fft = np.fft.fft

################################################################################
############################### Helpers ########################################
################################################################################

#copied from matploblib official tutorial
def make_ticklabels_invisible(fig):
    for i, ax in enumerate(fig.axes):
        #ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)
            
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
    f = np.asscalar(f) #convert to scalar
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

def drawDotRing(r):
    angles = np.arange(2*np.pi,step=0.05)
    print(angles)
    radii = [r for i in range(len(angles))]
    print(radii)
    
################################################################################
################################## Main ########################################
################################################################################

def debugPlot():
    '''The main fucntion for displaying real-time drawing'''
    
################################################################################
############################### Constants ######################################
################################################################################
    
    offset = 157
    startR = 0.1
    stepR = 0.1
    curTime = 0
    
################################################################################
############################ Interaction Class #################################
################################################################################
    
    class MouseStop:
        '''stop the animation loop when the user clicks'''
        def __init__(self, line):
            self.line = line
            self.stop = False
            self.xs = list(line.get_xdata())
            self.ys = list(line.get_ydata())
            self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
    
        def __call__(self, event):
            print('click', event)
            self.stop = True
            print('stop',self.stop)
    
################################################################################
############################### PyAudio ########################################
################################################################################

    CHUNK =  1024*2
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 #built-in microphone is monotone
    RATE = 16000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Pyaudio recording")
    
################################################################################
########################## MPL Initialization ##################################
################################################################################
    '''
    @var ax:  np line of volume over time
    @var ax2: np line of volume over frequency
    @var ax3: np polar graph of generated painting
    '''
    r = []
    theta = []
    area = []
    colors = theta 
    x_fft = np.linspace(0,RATE,CHUNK) #max freq is sampling rate 
    mpl.rcParams['toolbar'] = 'None' #disable ugly default toolbar
    
    #set the handdrawn style      
    with plt.xkcd():

        fig = plt.figure("colorfulNote")
        
        #arrange subplot positions using gridspec
        gs = GridSpec(5, 5)
        gs.update(wspace=0.05)
        ax2 = plt.subplot(gs[:, -1:])
        ax3 = plt.subplot(gs[:,:-1], polar=True,autoscale_on=False)
        
        #configue ax2 and ax3
        ax2.set_ylim(20,RATE/20) #at 0 line is discontinuous
        ax3.axis('on')
        ax3.grid(False)
        ax3.scatter(theta, r, c=colors, s=area, cmap=cm.cool)
        ax3.set_alpha(0.5) #alpha is the ratio of transparency
        
        #create line and text objects to be updated
        pitchText = ax2.text(0.05, 0.9, '')
        line_fft, = ax2.plot(np.random.rand(CHUNK),x_fft,  '-', lw=2)
       
        #bind click action with subplot
        first = MouseStop(line_fft)
        
        #configue the entire figure
        #fig.tight_layout()
        make_ticklabels_invisible(fig)
        plt.show(block=False)
        

    print('stream started')
    
################################################################################
########################## Animation Loop ######################################
################################################################################    
    
    res=[]
    while first.stop == False:
        data = stream.read(CHUNK,exception_on_overflow = False)
        data_int = struct.unpack(str(2*CHUNK)+'B',data)
        data_np = np.array(data_int, dtype='b')[::2] 
        #line.set_ydata(data_np)
        #fft
        y_fft = fft(data_int)
        #slice to get ride of conjugate and rescale
        scaled_y = np.abs(y_fft[:CHUNK]) * 2 / (128*CHUNK)
        line_fft.set_xdata(scaled_y)
        
        real_y = scaled_y[20:]
        freqs =line_fft.get_ydata()
        maxAmp = max(real_y)
        #index of the max frequency
        maxi = np.where(real_y==maxAmp)
        
        curFreq= freqs[maxi]+offset
        curPitch = fToNote(curFreq)
        avgAmp = np.asscalar(sum(np.abs(data_np))/len(data_np))
        pitchText.set_text(curPitch)

        #print("cur,avg:",curFreq,avgAmp)
        
        # print("calulating new data!")
        #process        
        newArea = convertToArea(avgAmp) #the second entry is numeric val
        newAngle = fToAngle(np.asscalar(curFreq))
        newR = startR + stepR * (curTime // 3)
        # print("A:",newArea)
        # print("theta:",newAngle)
        # print("r:",newR)
        # print("pitch:",curPitch)
        # print("**********\n")
        area.append(newArea)
        theta.append(newAngle)
        r.append(newR)
        ax2.text(2, 1,curPitch)
        ax3.scatter(theta, r, c=colors, s=area, cmap=cm.cool)
        #ax2.axhline(y=curFreq,xmin=0,xmax=800,c="red",linewidth=30,zorder=0)
                
        #make sure curFreq is in legal range
        #res.append((np.asscalar(curFreq%800),avgAmp))
        #update graph
        
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
            curTime += 1 #keep time
            
        except:
            print('stream stopped')
            break
       
################################################################################
########################## Export Data #########################################
################################################################################
    #write audio data to file
    f = open("data.txt","w")
    for freq in res:
        f.write(str(freq))
        f.write("\n")
    f.close()
    
#save png file
    extent = ax3.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig('colorful_drawing.png', bbox_inches=extent)

