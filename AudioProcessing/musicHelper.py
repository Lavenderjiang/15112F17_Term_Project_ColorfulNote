#author: Lavender Jiang
#contact: yaoj@andrew.cmu.edu
#15112F17 Term Project

def colorListGen(data):
    res = []
    print(data.ringType)
    if data.ringType == "pure": num = 1
    elif data.ringType == "bead": num = 2
    elif data.ringType == "wavy": num = 4
    diffList = data.diffList
    freqs = data.anaCycle.freq
    for i in range(num):
        curFreq = max(freqs)
        color = freqToColour(curFreq)
        color = rgbToHex(color)
        res.append(color)
        freqs.pop(freqs.index(curFreq))

        #minI = diffList.index(min(diffList))
        #curFreq = freqs[minI]
        #print("analyzing this:",curFreq)
        #color = freqToColour(curFreq)
        #res.append(color)
        #diffList.pop(minI)
    data.colors = res

def testColorListGen():
    class Struct(): pass
    data = Struct()
    data.colors=[]
    data.diffList=[1,2,1,0]
    data.ringType = "wavy"
    data.freqs = [547.8158280410357, 378.59257449926736, 409.85784074255025, 472.38837322911604, 448.9394235466534]
    colorListGen(data)
    print(data.colors)

    data.ringType = "bead"
    data.diffList = [0,0,8,3]
    data.freqs = [412.20273571079633, 407.1221299462628, 412.20273571079633, 389.1446018563747, 438.38739618954565]
    colorListGen(data)
    print(data.colors)

    data.ringType = "wavy"
    data.diffList = [4,4,3,2]
    data.freqs = [266.42843185149, 615.4269662921347, 261.34782608695605, 547.8158280410357, 261.34782608695605]
    colorListGen(data)
    print(data.colors)

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
    return abs(halfStepsA-halfStepsB)

def testHalfStepsBetween():
    assert(halfStepsBetween("F1","C1") == 5)
    assert(halfStepsBetween("G4","C1") == 43)
    assert(halfStepsBetween("G4","F#4") == 1)
    assert(halfStepsBetween("F#4","G4") == 1)
    print("passed!")

def NoteListToType(noteList,data):
    threshold = 2
    count = 0
    diffList = []
    #the last note has no next note
    for i in range(len(noteList)-1):
        prev = noteList[i]
        nex = noteList[i+1]
        distance = halfStepsBetween(prev,nex)
        diffList.append(distance)
        if distance > threshold: count += 1
    #print("count",count)
    if count <=1: data.ringType="pure"
    elif count <= 2: data.ringType="bead"
    else: data.ringType= "wavy"
    print(diffList)
    print(data.ringType)
    data.diffList=diffList

def testConvertType():
    class Struct(): pass
    data = Struct()
    data.type=""
    data.diffList=[]
    NoteListToType(['B3', 'B3', 'F#5', 'C4', 'C4'],data)
    return


    assert(changesInHalfStepsToType(['F3', 'E4', 'F4', 'A#4', 'F4'])=="wavy")
    assert(changesInHalfStepsToType(['A4', 'C5', 'E4', 'G#4', 'E4'])=="wavy")
    assert(changesInHalfStepsToType(['C5', 'B4', 'A4', 'A4', 'C4'])=="pure")
    assert(changesInHalfStepsToType(['F#5', 'C4', 'C4', 'C4', 'B4'])=="bead")
    assert(changesInHalfStepsToType(['C#5', 'F#4', 'G#4', 'A#4', 'A4'])=="pure")
    assert(changesInHalfStepsToType(['C4', 'D#5', 'C4', 'C#5', 'C4'])=="wavy")
    print("passed!")

def strenToIncR(stren,data):
    standard = {"low":20,"medium":30,"high":40,"crazy":50}
    if stren < 30: key = "low"
    elif stren < 50: key = "medium"
    elif stren < 60: key = "high"
    else: key = "crazy"
    data.incR = standard[key]
    return standard[key] 

def testConvertToInc():
    assert(convertToInc(40)==10)
    assert(convertToInc(65)==20)
    print("passed!")






