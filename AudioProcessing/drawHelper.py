#author: Lavender Jiang
#contact: yaoj@andrew.cmu.edu
#15112F17 Term Project

################################################################################
############################### Imports ########################################
################################################################################
from math import log2
import math
import decimal
###############################################################################
############################### Helpers ########################################
################################################################################
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

################################################################################
############################### Drawing ########################################
################################################################################

def drawCircleRing(canvas,zeroX,zeroY,innerR,outerR,color,bgColor="black",startAngle=0,spacing=0,width=0):
    '''

    Given the innerR and outerR of a ring, draw a ring made of circles on Canvas.

    # @param zeroX, zeroY: cartesian coordinate of the center of the ring
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

    
    ####!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #canvas.create_oval(zeroX-outerR,zeroY-outerR,zeroX+outerR,zeroY+outerR,fill=bgColor)

    res = []
    #startAngle = 0
    for i in range(totalCircle):
        angle = startAngle + i * (unitFillAngle + angleWithSpace)
        cx,cy = polarToCartesian(midR,angle)
        #coordinate offset for different center
        cx += zeroX
        cy += zeroY
        i = canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=color,width=width)
        #print("item",i)
        res.append(i)
    #print("res",res)
    return res


def drawPureRing(data,canvas,zeroX,zeroY,innerR,outerR,colours,startAngle=0,spacing=0.2):
    '''
    Draw method for colorfulBeads class. Three rings of circle, with each circle outlined by
    their deeper color, is drawn on canvas.

    @param: see drawCircleRingOfCircles() docstring

    '''
    ringCount = 2
    innerColor, bgColor = colours[0],"orange"
    r = (outerR - innerR) 
    unitRange = r / ringCount
    toppingRatio = 0.2

    cx, cy = zeroX, zeroY
    # drawCircleRing(canvas,cx,cy,r+unitRange,r + 2*unitRange,innerColor,bgColor,startAngle)
    # drawCircleRing(canvas,cx,cy,r,r + unitRange,innerColor,bgColor,startAngle)
    drawCircleRing(canvas,cx,cy,innerR+unitRange, innerR + 2*unitRange, innerColor,bgColor,startAngle,width=3)
    drawCircleRing(canvas,cx,cy,innerR, innerR + unitRange, innerColor,bgColor,startAngle,width=3)

def drawColorfulBeads(data,canvas,zeroX,zeroY,innerR,outerR,colours,startAngle=0,spacing=0.2):
    '''
    Draw method for colorfulBeads class. Three rings of circle, with each circle outlined by
    their deeper color, is drawn on canvas.

    @param: see drawCircleRingOfCircles() docstring

    '''
    ringCount = 2
    innerColor, outerColor, bgColor = colours[0],colours[1],"black"
    r = (outerR - innerR) 
    unitRange = r / ringCount
    toppingRatio = 0.2

    cx, cy = zeroX, zeroY
    #print("Here;s info for beads!")
    #print("innerR",innerR,"outerR",outerR)
    drawCircleRing(canvas,cx,cy,innerR+unitRange,innerR + 2*unitRange,outerColor,bgColor,startAngle)
    drawCircleRing(canvas,cx,cy,innerR,innerR + unitRange,innerColor,bgColor,startAngle)


def drawCircleRingOfCircles(data,canvas,zeroX,zeroY,innerR,outerR,colours,startAngle=0,spacing=0.7):
    '''

    Draw method for the wavy ring class. A very colorful flower-like pattern is drawn.
    
    @param colours: a list of strings for coloring the wavy ring
    @param startAngle: the polar angle of the center of the first circle
    @param spacing: see docstring for drawCircleRing() 
    @var overlap: the percentage of overlapped radius between two adjacent circles
    @var dressingR: the radius of the extending circle 
    @var toppingR: the radius of the smaller circle inside the extending circle
    
    Note: 
        1) When adding rings dynamically, add ring objects to data instead of calling
        this draw function. This helps with scaling the image when in need.
        2) startAngle is used for animating the rotating ring.

    '''
    innerColor, midColor, outerColor, bgColor = colours[0],colours[1],colours[2],colours[3]
    r = (outerR - innerR) / 2
    midR = (outerR + innerR) / 2
    halfAngle = solveAngle(midR,midR,r)
    fullAngle = 2 * halfAngle
    angleWithSpace = fullAngle + spacing * fullAngle

    #totalFillAngle = 2*math.pi % fullAngle
    totalCircle = int( (2*math.pi) // angleWithSpace)
    totalFillAngle = (2*math.pi) - totalCircle * angleWithSpace

    #totalCircle = int( (2*math.pi - spacing*fullAngle*totalCircle) // fullAngle)
    unitFillAngle = totalFillAngle/totalCircle 

    overlap = 0.5
    dressingR = solveLength(midR, midR, unitFillAngle + angleWithSpace)/2
    dressingR = dressingR * (1+overlap)
    toppingRatio = 0.8
    toppingR = dressingR * toppingRatio
    #toppingColor = "orange"

    items = []
    for i in range(totalCircle):
        angle = startAngle + i * (unitFillAngle + angleWithSpace)
        cx,cy = polarToCartesian(midR,angle)
        cx += zeroX
        cy += zeroY
        #coordinate offset for different center

        item1 = canvas.create_oval(cx-dressingR,cy-dressingR, dressingR+cx,dressingR+cy,fill=outerColor)
        print("item1",item1)
        item2 = canvas.create_oval(cx-toppingR,cy-toppingR, toppingR+cx,toppingR+cy,fill=midColor)
        item3 = drawCircleRing(canvas,cx,cy,r/3,r,innerColor,bgColor)
        add = [item1,item2]
        add.extend(item3) #item3 is list
        items.extend(add)

    if data.addFlag == True:
        data.items.append(items)

################################################################################
############################### Ring Class #####################################
################################################################################

class firstCircle(object):
    def __init__(self,canvas,zeroX,zeroY,color,radius):
        self.canvas=canvas
        self.color = color
        self.zeroX = zeroX
        self.zeroY = zeroY
        self.r = radius
        self.angle = 0

    def draw(self,data):
        cx = self.zeroX
        cy = self.zeroY
        r=self.r
        item = self.canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=self.color)
        if data.addFlag == True:
            data.items.append([item])

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
        self.delete = False

    def translate(self,coord):
        '''move center'''
        pass

class wavyRing(musicRing):

    def draw(self,data):
        if self.delete == True: pass
        drawCircleRingOfCircles(data,self.canvas,self.zeroX,self.zeroY,
                                self.innerR,self.innerR + 2*self.unitR,
                                self.colors,self.angle)

class colorfulBeads(musicRing):
    '''
    Has most pitch changes in an analysis cycle
    '''
    def draw(self,data):
        if self.delete == True: pass
        drawColorfulBeads(data,self.canvas,self.zeroX,self.zeroY,
                          self.innerR,self.outerR,self.colors,self.angle)


class pureRing(musicRing):

    def draw(self,data):
        if self.delete == True: pass
        drawPureRing(data,self.canvas,self.zeroX,self.zeroY,
                     self.innerR,self.outerR,self.colors,self.angle)
