import pyaudio
from array import array
from struct import pack #used to unpack audio data into integer
import numpy as np
np.set_printoptions(threshold=np.nan) #print full np array
import matplotlib.pyplot as plt
import wave
import struct



#from IPython import get_ipython
#get_ipython().run_line_magic('matplotlib', 'tk')
#%matplotlib tk #display separate window


def play(file):
    CHUNK = 1024 #bytes

    wf = wave.open(file,"rb")

    p = pyaudio.PyAudio() #create a pyaudio object

    stream = p.open(
    format = p.get_format_from_width(wf.getsampwidth()),
    channels = wf.getnchannels(),
    rate = wf.getframerate(),
    output=True
    )

    data = wf.readframes(CHUNK)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()

def record(outputFile):
    CHUNK =  1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 #built-in microphone is monotone
    RATE = 44100
    RECORD_SECONDS = 1

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
        print(data_int)
        frames.append(data)
        print("******************\n")

    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(outputFile,"wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def test():
    #plt.ion()
    fig, ax = plt.subplots(1, figsize=(15, 7))
    
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
    
    # create a line object with random data
    line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=2)
    
    # basic formatting for the axes
    ax.set_title('AUDIO WAVEFORM')
    ax.set_xlabel('samples')
    ax.set_ylabel('volume')
    ax.set_ylim(0, 255)
    ax.set_xlim(0, 2 * CHUNK)
    plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

    plt.show(block=False)
    
    print('stream started')
    
    while True:
        data = stream.read(CHUNK)
        data_int = struct.unpack(str(2*CHUNK)+'B',data)
        #print(data_int)
        data_np = np.array(data_int, dtype='b')[::2] 
        #print(data_np)
        line.set_ydata(data_np)
    
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
           # frame_count += 1
            #plt.pause(0.1)
            
        except:
            print('stream stopped')
            #print('average frame rate = {:.0f} FPS'.format(frame_rate))
            break


def offset(t):
    res = []
    for i in t:
        i = i%256
        res.append(i)
    return tuple(res)

def testplot():
    CHUNK = 1024 * 4
    FORMAT = pyaudio.paInt16 #16-BYTE
    CHANNELS = 1 #MONOSOUND
    RATE = 44100 #44.1 kHz


    p = pyaudio.PyAudio()

    stream = p.open(
        format = FORMAT,
        channels = CHANNELS,
        rate = RATE,
        input = True,
        output = True,
        frames_per_buffer=CHUNK
    )
    
    data = stream.read(CHUNK)
    
    print(data)
   
        
 
 
 
 
 
 
 
 
 
 
 
 
 
 
