import pyaudio
from array import array
from struct import pack #used to unpack audio data into integer
from ast import literal_eval
import numpy as np
np.set_printoptions(threshold=np.nan) #print full np array
import matplotlib.pyplot as plt
import wave
import struct
fft = np.fft.fft

def debugPlot():
    offset = 157
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
    
    #plt.ion()
    fig, (ax,ax2) = plt.subplots(2, figsize=(15, 7)) #two figures
    
    CHUNK =  1024*2
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 #built-in microphone is monotone
    RATE = 16000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    #output=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    # variable for plotting
    x = np.arange(0, 2 * CHUNK, 2)
    x_fft = np.linspace(0,RATE,CHUNK)
    # create a line object with random data
    line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=2)
    line_fft, = ax2.plot(x_fft, np.random.rand(CHUNK), '-', lw=2)
    
    first = MouseStop(line)
    
    # basic formatting for the axes
    ax.set_title('AUDIO WAVEFORM')
    ax.set_xlabel('samples')
    ax.set_ylabel('volume')
    ax.set_ylim(0, 255)
    ax.set_xlim(0, 2 * CHUNK)
    plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

    ax2.set_title('Amplitude over frequency')
    ax2.set_xlabel('freq')
    ax2.set_ylabel('volume')
    ax2.set_xlim(20,RATE/20) #at 0 line is discontinuous
    
    plt.show(block=False)
    
    print('stream started')
    
    res=[]
    while first.stop == False:
        data = stream.read(CHUNK)
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
        maxAmp = max(real_y)
        #index of the max frequency
        maxi = np.where(real_y==maxAmp)
        curFreq= freqs[maxi]+offset
        avgAmp = sum(np.abs(data_np))/len(data_np)
        print("cur,avg:",curFreq,avgAmp)
        
        #make sure curFreq is in legal range
        res.append((np.asscalar(curFreq%800),avgAmp))
        
        #update graph
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
            
        except:
            print('stream stopped')
            break
    
    #write audio data to file
    f = open("data.txt","w")
    for freq in res:
        f.write(str(freq))
        f.write("\n")
    f.close()


def extractData():
    f = open("data.txt","r")
    res = []
    #use literal_eval to safety turn string back to tuple
    for line in f:
        res.append(literal_eval(line))
    print(res)