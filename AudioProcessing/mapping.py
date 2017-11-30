import pyaudio
from array import array
from struct import pack #used to unpack audio data into integer
from ast import literal_eval
from math import log2
from random import uniform
from random import randint
from pylab import *
from matplotlib.gridspec import GridSpec
import numpy as np
np.set_printoptions(threshold=np.nan) #print full np array
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import wave
import struct
fft = np.fft.fft

#copied from matploblib official tutorial
def make_ticklabels_invisible(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)

def debugPlot():
    mpl.rcParams['toolbar'] = 'None'
    offset = 157
    startR = 0.1
    stepR = 0.1
    curTime = 0
    class MouseStop:
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
    
    fig = plt.figure()
    
    gs = GridSpec(5, 5)
    gs.update(wspace=0.05)
    ax = plt.subplot(gs[0, :])
    # identical to ax1 = plt.subplot(gs.new_subplotspec((0,0), colspan=3))
    ax2 = plt.subplot(gs[1:, -2:])
    
    
    
    ax3 = plt.subplot(gs[1:,:-2], polar=True)
    ax3.axis('off')
    # ax3.plot(theta, r)
    # ax3.set_rmax(3)
    # ax3.set_rticks([0.5, 1, 1.5, 2])  # less radial ticks
    # ax3.set_rlabel_position(-22.5)  # get radial labels away from plotted line
    ax3.grid(True)
    
    r = []
    theta = []
    area = []
    colors = theta 

    ax3.scatter(theta, r, c=colors, s=area, cmap=cm.cool)
    ax3.set_alpha(0.5) #alpha is the ratio of transparency
    
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

    print("* recording")

    # variable for plotting
    x = np.arange(0, 2 * CHUNK, 2)
    #print(x)
    x_fft = np.linspace(0,RATE,CHUNK)
    # create a line object with random data
    line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=2)
    line_fft, = ax2.plot(x_fft, np.random.rand(CHUNK), '-', lw=2)
    
    first = MouseStop(line)
    
    # basic formatting for the axes
    ax.set_title('AUDIO WAVEFORM')
    #ax.set_xlabel('samples')
    #ax.set_ylabel('volume')
    ax.set_ylim(0, 255)
    ax.set_xlim(0, 2 * CHUNK)
    plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

    #ax2.set_title('Amplitude over frequency')
    #ax2.set_xlabel('freq')
    #ax2.set_ylabel('volume')
    ax2.set_xlim(20,RATE/20) #at 0 line is discontinuous
    
    #fig.tight_layout()
    make_ticklabels_invisible(fig)
    plt.show(block=False)
    
    print('stream started')
    
    res=[]
    while first.stop == False:
        #print("in while loop!")
        data = stream.read(CHUNK,exception_on_overflow = False)
        data_int = struct.unpack(str(2*CHUNK)+'B',data)
        #print(data_int)
        data_np = np.array(data_int, dtype='b')[::2] 
        #print(data_np)
        line.set_ydata(data_np)
        #fft
        y_fft = fft(data_int)
        #slice to get ride of conjugate and rescale
        scaled_y = np.abs(y_fft[:CHUNK]) * 2 / (128*CHUNK)
        line_fft.set_ydata(scaled_y)
        
        real_y = scaled_y[20:]
        freqs =line_fft.get_xdata()
        print("type",type(freqs))
        print(np.array([1,2,3]))
        maxAmp = max(real_y)
        #index of the max frequency
        maxi = np.where(real_y==maxAmp)
        print("maxi",maxi,freqs[maxi])
        
        
        curFreq= freqs[maxi]+offset
        curPitch = fToNote(curFreq)
        avgAmp = np.asscalar(sum(np.abs(data_np))/len(data_np))
        #print("cur,avg:",curFreq,avgAmp)
        
        print("calulating new data!")
        #process        
        newArea = convertToArea(avgAmp) #the second entry is numeric val
        newAngle = fToAngle(np.asscalar(curFreq))
        newR = startR + stepR * (curTime // 3)
        print("A:",newArea)
        print("theta:",newAngle)
        print("r:",newR)
        print("pitch:",curPitch)
        print("**********\n")
        area.append(newArea)
        theta.append(newAngle)
        r.append(newR)
        ax3.scatter(theta, r, c=colors, s=area, cmap=cm.cool)
        
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
       
    
    #write audio data to file
    f = open("data.txt","w")
    for freq in res:
        f.write(str(freq))
        f.write("\n")
    f.close()

#copied from 112 course website
import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#Detection Range: A0(27.5Hz) ~ G5(783Hz)
#59 half steps in total
def fToNote(f):
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
    unitAngle = 2*np.pi/59
    print(unitAngle)
    C0 = 16.35
    halfStepsToC0 = roundHalfUp(12*log2(f/C0))
    halfStepsToA0 = halfStepsToC0 - 9
    startAngle = unitAngle * halfStepsToA0
    #fAngle = randint(0,2*np.pi)
    #print(startAngle)
    # print(startAngle+unitAngle)
    fAngle = uniform(startAngle,startAngle+unitAngle)
    #print("degree:",360/(2*np.pi)*fAngle)
    return fAngle

def testAngleConversion():
    fToAngle(800) #around 360 degree
    fToAngle(27.5) #around 0 degree
    fToAngle(400) #around 300 degree

def convertToArea(stren):
    threshold = 5
    loudness = ["tiny","low","medium","high"]
    radii = [30,50,100,150]
    if stren<5: return 5
    elif stren<30: res = randint(5,30)
    elif stren<50: res = randint(30,50)
    elif stren<60: res = randint(50,100)
    else: res = randint(100,150)  
    return res
    
def testAreaConversion():
    print(convertToArea(42.7)) #('low',5)
    print(convertToArea(68.9)) #('high', 20)
    
def extractData():
    f = open("data.txt","r")
    res = []
    #use literal_eval to safety turn string back to tuple
    for line in f:
        res.append(literal_eval(line))
    #first is frequency(0~800), second is strength(0~64)
    for d in res:
        freq = d[0]
        pitch = fToNote(freq)
        print(pitch)
        stren = d[1]
    #print(res)