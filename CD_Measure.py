# -*- coding: utf-8 -*-
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2022 Dan Miel                                           *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************
"""
This can be used to see information about part features or to measure between features.
Select one feature to view information or two features to see distance between them.
The distance also show the x ,y ,z between them.

"""


import os
import FreeCAD
import FreeCADGui
from PySide import QtGui, QtCore
from PySide.QtGui import *
from numpy.core.numeric import False_
#import a2p_constraints
#import a2p_constraintDialog
import math
import numpy as np
#import DraftGeomUtils 
class globaluseclass:
    def __init__(self, name):
        self.sONOFF = 'off'
        self.measureEnabled = False
        self.HiddenFeaturesEnabled = False
        self.msg = ''
        self.header = ''
g = globaluseclass("g")


class info:
    def __init__(self):
        self.area = 0

        self.centerofmass = 0
        self.bodyname = ''
        self.entity = None
        self.fname = ''
        self.type = ''  #Circle or Line
        self.length = 0 
        self.Name = "No info"
        self.normal = 0
        self.perimeter = 0
        self.point1 = 0
        self.point2 = 0
        self.radius = 0
        self.shape = None
        self.x = 'n'
        self.y = 'n'
        self.z = 'n'
        self.xyz = 'n'

    def clear(self):
        self.area = 0
        self.centerofmass = 0
        self.bodyname = ''
        self.entity = None
        self.fname = ''
        self.type = ''
        self.length = 0 
        self.Name = " No info"
        self.normal = 0
        self.perimeter = 0
        self.point1 = 0
        self.point2 = 0
        self.radius = 0
        self.shape = None
        self.x = 'n'
        self.y = 'n'
        self.z = 'n'
        self.xyz = 'n'


    def __str__(self):
        return f'{self.Name}'
f0 = info() # Two features are needed so created a class for features 1 and 2
f1 = info()

class measureClass:
    def __init__(self):
        pass
    def measureSelected(self):
        selections = FreeCADGui.Selection.getSelectionEx()
        selectionslen = len(selections)
        featsInf0 = len(selections[0].SubElementNames)
        features0 = selections[0].Object.Shape
        f0.clear()
        f1.clear()
        g.header = ''
        g.msg = ''
        
        if selectionslen == 1 and featsInf0 == 0:
            # If 1 selection but no features are selected then a is body selected.
            ''' Mesure body'''
            name = selections[0].Object.Label
            totarea = self.convertArea([features0.Area])[0]
            totVolume = self.convertVolume([features0.Volume])[0]
            g.msg = '{}\nArea = {}\nVolume = {}'.format(name, totarea, totVolume)
            return
        numoffeats = 0
        for o in selections: # Find number of selected surfaces
            numoffeats = numoffeats + len(o.SubElementNames)
        if numoffeats > 2: # More than 2 features
            self.check2plus(selections,selectionslen)
        else:
            #At least 1 feature is selected so fill feature f0 with infomation.
            f0.bodyname = selections[0].Object.Label
            f0.fname = selections[0].SubElementNames[0]
            f0.shape = selections[0].Object.Shape
            if "Vertex" in f0.fname:self.getvertex(f0)
            if "Face" in f0.fname:self.getface(f0)
            if "Edge" in f0.fname:self.getedge(f0)

            if selectionslen == 1 and featsInf0 == 1:
                ''' If 1 feature is selected then measure feature.'''
                if 'Vertex' in f0.fname:
                    g.msg = 'x = {}\ny = {}\ny = {}'.format(f0.x, f0.y, f0.z)

                if 'Face' in f0.fname:
                    if 'Sphere' in f0.type or 'Cylinder' in f0.type:
                        g.msg = 'Radius = {}\nCenter\nx = {}\ny = {}\nz = {}'.format(f0.radius, f0.x ,f0.y ,f0.z)
                    if 'Plane' in f0.type:
                    
                        area = self.convertArea([f0.area])
                        perimeter = self.convertLen([f0.perimeter])
                        g.msg  = 'Area = {}\nPerimeter = {}'.format(area[0], perimeter[0])
                if 'Edge' in f0.fname:
                    if 'Line' in f0.type:
                        cx, cy, cz = self.convertLen(f0.xyz)
                        length = self.convertLen([f0.length])[0]
                        g.msg = 'Length = {}\nCenter of line\nx = {}\ny = {}\nz = {}'.format(length, cx, cy, cz)
                    if 'Circle' in f0.type: 
                        circ = self.convertLen([f0.length])[0]
                        radius = self.convertLen([f0.radius])[0]
                        g.msg = 'Radius = {}\nEdge Length = {}\nx = {}\ny = {}\nz = {}'.format(radius, circ, f0.x, f0.y, f0.z)

                    if 'Spline' in f0.type:
                        g.msg ='Spline Not added.\n2022-05-04' # A2 is not using these
                if g.msg == '':
                    g.header = '\nI cannot measure that feature'
                else:
                    g.header = '{} of {}'.format(f0.fname, f0.bodyname)

            
        

        
            featsin1 = 0
            if selectionslen == 2:
                #If selection length is 2
                    featsin1 = len(selections[1].SubElementNames) #Check the number of entities in selection 1.

            ''' sort to see if two seperate features are selected. ''' 
            if selectionslen == 1 and featsInf0 == 2 or selectionslen == 2 and featsInf0 == 1 and featsin1 == 1:
                if selectionslen == 1: # If both features are on the (same body) get f1 feature
                    f1.fname = selections[0].SubElementNames[1]
                    f1.shape = selections[0].Object.Shape
                else: # If the features are in a (different bodys) get f1 (featurre1 class)
                    f1.fname = selections[1].SubElementNames[0]
                    f1.shape = selections[1].Object.Shape
                # Get information for second feature
                if 'Vertex' in f1.fname:self.getvertex(f1)
                if "Face" in f1.fname:self.getface(f1)
                if "Edge" in f1.fname:self.getedge(f1)
                # Next three line send feature information to seperate sections
                if 'Vertex' in f0.fname or 'Vertex' in f1.fname:
                    self.checkVertexes()
                elif 'Edge' in f0.fname or 'Edge' in f1.fname:
                    self.checkEdges()
                elif 'Face' in f0.fname or 'Face' in f1.fname:
                    self.checkSurfaces()
        form1.txtboxReport.setText(g.header + '\n' + g.msg)
            #end of program


    def checkVertexes(self):
        # Check Vertexes
        if "Vertex" in f0.fname and 'Vertex' in f1.fname:
            g.header = 'Vertex to Vertex'
        featnames = f0.fname + f1.fname
        feattypes = f0.type + f1.type
        if 'Edge' in featnames:
            if 'Circle' in feattypes:
                g.header = 'Vertex to Circle center'
            if 'Line' in feattypes:
                g.header = 'Vertex to mid Line'
        if 'Face' in featnames:
            if "Sphere" in feattypes:
                g.header = 'Vertex to Sphere center'
        g.msg = self.getMsgBetween()    
        
    def checkEdges(self):
        # Check edges
        if 'Edge' in f0.fname and 'Edge' in f1.fname:
            g.header = 'edge edge'
            if 'Line' in str(f0.type) and 'Line' in str(f1.type):
                vec1 = f0.entity.Vertex2.Point - f0.entity.Vertex1.Point
                vec2 = f1.entity.Vertex2.Point - f1.entity.Vertex1.Point
                angle = vec1.getAngle(vec2)
                test = str(angle)[0:8]
                g.header = f0.fname + ' and ' + f1.fname
                if angle == math.pi or angle == 0.0:                    
                    g.msg = 'Lines are parallel'
                elif test == '1.570796' or test == '1.570796' :
                    g.msg = 'Lines are normal (90 degrees) to each other'
                else:
                    g.msg = "Lines are not parallel"
                
            if 'Circle' in str(f0.type) and 'Circle' in str(f1.type):
                g.header = 'Center to Center'
                g.msg = self.getMsgBetween()
                if 'Line' in f0.type or 'Line' in f1.type:
                    g.header = 'Mid line to circle center'
                    g.msg = self.getMsgBetween()
            feattypes = f0.type + f1.type
            if 'Line' in feattypes and 'Circle' in feattypes:
                g.header = 'Circle to mid line'
                g.msg = self.getMsgBetween()
            totlen = self.convertLen([f0.length + f1.length])[0]
            g.msg = g.msg + '\nTotal Length = ' + totlen

        featnames = f0.fname + f1.fname
        feattypes = f0.type + f1.type
        if 'Face' in featnames:
            if 'Sphere' in feattypes:
                if 'Line' in feattypes:
                    g.header = 'Mid Line to Sphere Center'
                if 'Circle' in feattypes:
                    g.header = 'Curve center to Sphere center'
            g.msg = self.getMsgBetween()

    def checkSurfaces(self):
        #Report surfaces
        if 'Face' in f0.fname and 'Face' in f1.fname:
            if 'Plane' in f0.type and'Plane' in f1.type:
                myangle = math.degrees( f0.normal.getAngle( f1.normal))
                anglestring = self.convertAngle([myangle])
                g.header = f0.fname + ' and ' + f1.fname
                if myangle == 90 or myangle == 270:
                    g.msg = 'Planes are Normal ' + anglestring[0]
                elif myangle == 0 or myangle == 180:
                    d = f0.entity.Surface.projectPoint(f1.entity.valueAt(0, 0), 'Distance')                        
                    dists = self.convertLen([d[0]])
                    g.msg = 'Planes are Parallel\nDist = ' + dists[0]
                else:
                    g.msg = "angle between faces = " + anglestring[0]
            if 'Sphere' in f0.type and'Sphere' in f1.type:
                g.header = 'Sphere center to Sphere center'
                g.msg = self.getMsgBetween()
            area = self.convertArea([f0.area + f1.area])[0]
            perimeter = self.convertLen([f0.perimeter + f1.perimeter])[0]
            g.msg = g.msg + '\nTotal Area = {}\nPerimeters = {}'.format(area, perimeter)

    def check2plus(self, selections, selectionslen):
        # check when selections are 3 or more
        numoffeats = 0
        for o in selections:
            numoffeats = numoffeats + len(o.SubElementNames)
        allfaces = True
        alledges = True
        totlen = 0
        totarea = 0
        for num in range(0,selectionslen):
            obj = selections[num]
            subelen = len(obj.SubElementNames)
            for num2 in range(0,subelen):
                elementname =obj.SubElementNames[num2]
                f0.shape = obj.Object.Shape
                f0.fname = elementname
                if 'Face' in elementname:
                    self.getface(f0)
                    totarea = totarea + f0.area
                    totlen = totlen + f0.perimeter
                    alledges = False
                if 'Edge' in elementname:
                    self.getedge(f0)
                    totlen = totlen + f0.length
                    allfaces = False
                if 'Vertex' in elementname:
                    alledges = False
                    allfaces= False
        if allfaces:
            myArea = self.convertArea([totarea])[0]
            myPrim = self.convertLen([totlen])
            g.header = 'Total of {} Faces'.format(numoffeats)
            g.msg = 'Total Area = {}\.Perimeters{}'.format(myArea,myPrim)
        if alledges:
            myLength = self.convertLen([totlen])[0]
            g.header = 'Total Length of {} Edges'.format(numoffeats)
            g.msg = 'Length = ' + myLength

    def getMsgBetween(self):
        # Finds distant and x y z, then returns results in a string
        xyzd = self.getpointsdistance(f0.xyz, f1.xyz)
        x, y, z, dist = self.convertLen(xyzd)
        lmsg = "Distance = {}\nx = {}\ny = {}\nz = {}".format(dist, x, y, z)
        return(lmsg)
            
    def shortest_distance(self, x1, y1, z1, a, b, c, d):
        
        d = abs((a * x1 + b * y1 + c * z1 + d))
        e = (math.sqrt(a * a + b * b + c * c))

    def getface(self, ci): # ci is for class.info
        num = int(ci.fname[4:]) -1
        face = ci.shape.Faces[num]
        ci.entity = face
        ci.type = str(face.Surface)
        ci.normal = face.normalAt(0, 0)
        ci.area = face.Area
        perm = 0
        for edge in face.Edges:
            perm = perm + edge.Length
        ci.perimeter = perm
        ci.area = face.Area
        if 'Cylinder' in ci.type or 'Sphere' in ci.type:
            ci.radius = self.convertLen([ci.entity.Surface.Radius])[0]
            self.getvector(ci.entity.Surface.Center, ci)
        return()


        
    def getedge(self, ci): #ci = class info
        num = int(ci.fname[4:]) -1
        edge = ci.shape.Edges[num]
        ci.entity = edge
        ci.length = edge.Length
        ci.type = str(edge.Curve)
        if 'Line' in ci.type:
            ci.xyz = edge.CenterOfMass
        if 'Circle' in ci.type:
            ci.radius = edge.Curve.Radius
            self.getvector(edge.Curve.Center, ci)
        return()
    
    def getvertex(self, p3):
        num = int(p3.fname[6:]) -1
        vertex = p3.shape.Vertexes[num]
        p3.xyz = vertex.Point
        p3.x, p3.y, p3.z = self.convertLen(vertex.Point)
        return(p3)
    
    def getvector(self, vector, ci):
        ci.xyz = vector
        ci.x, ci.y, ci.z = self.convertLen(vector)
        return(ci)

    def convertLen(self, listofvalues):
        anslist = []
        for e in listofvalues:
            string = FreeCAD.Units.Quantity(e, FreeCAD.Units.Length).UserString
            anslist.append(string)
        return(anslist)

    def convertArea(self, listofvalues):
        anslist = []
        for e in listofvalues:
            string = FreeCAD.Units.Quantity(e, FreeCAD.Units.Area).UserString
            anslist.append(string)
        return(anslist)

    def convertVolume(self, listofvalues):
        anslist = []
        for e in listofvalues:
            string = FreeCAD.Units.Quantity(e, FreeCAD.Units.Volume).UserString
            anslist.append(string)
        return(anslist)

    def convertAngle(self, listofvalues):
        anslist = []
        for e in listofvalues:
            string = FreeCAD.Units.Quantity(e, FreeCAD.Units.Angle).UserString
            anslist.append(string)
        return(anslist)

    def getpointsdistance(self, arraypoint0, arraypoint1):
        x0, y0, z0 = arraypoint0
        x1, y1, z1 = arraypoint1
        larg = 0
        if x0< x1:
            larg = larg + 1
        if y0< y1:
            larg = larg + 1
        if larg == 0:
            lengx = x0 - x1
            lengy = y0 - y1
            lengz = z0 - z1
        else:
            lengx = x1 - x0
            lengy = y1 - y0
            lengz = z1 - z0
        ''' Calulate distant between points '''
        p1 = np.array([x0, y0, z0])
        p2 = np.array([x1, y1, z1])
        squared_dist = np.sum((p1-p2)**2, axis = 0)
        distance = np.sqrt(squared_dist)
        return([lengx, lengy, lengz, distance])

modmeasure = measureClass()


class formMain(QtGui.QMainWindow):

    def __init__(self, name):
        self.name = name
        super(formMain, self).__init__()
        self.setWindowTitle('Measure')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(300, 150, 300, 200)
        self.setStyleSheet("font:10pt arial MS")

        self.txtboxReport = QtGui.QTextEdit(self)
        self.txtboxReport.setGeometry(5, 50, 650, 90) # xy, wh

        self.btnOpenViewer = QtGui.QPushButton(self)
        self.btnOpenViewer.move(10, 5)
        self.btnOpenViewer.setFixedWidth(100)
        self.btnOpenViewer.setFixedHeight(28)
        self.btnOpenViewer.setToolTip("Clear")
        self.btnOpenViewer.setText("Clear")
        self.btnOpenViewer.clicked.connect(lambda:self.ClearAll())

        self.btnCloseForm = QtGui.QPushButton(self)
        self.btnCloseForm.move(120, 5)
        self.btnCloseForm.setFixedWidth(100)
        self.btnCloseForm.setFixedHeight(28)
        self.btnCloseForm.setToolTip("Close this form.")
        self.btnCloseForm.setText("Close")
        self.btnCloseForm.clicked.connect(lambda:self.closeme())

    def ClearAll(self):
        form1.txtboxReport.setText('')
        FreeCADGui.Selection.clearSelection()


    def resizeEvent(self, event):
        # resize table
        formx = self.width()
        formy = self.height()
        self.txtboxReport.resize(formx - 20, formy - 60)

    def showme(self, msg):
        self.txtboxReport.setText(msg)
        self.show()
        selObv.SelObserverON
        if len(FreeCADGui.Selection.getSelectionEx()) > 0:
            modmeasure.measureSelected()

    def closeme(self):
        selObv.SelObserverOFF()
        self.close()

    def closeEvent(self, event):
        selObv.SelObserverOFF()
        print('Shut down in closeEvent')
form1 = formMain('form1')

class SelObserver:
    def __init__(self):
        pass
    def SelObserverON(self):
        if g.sONOFF != 'on':
            FreeCADGui.Selection.addObserver(selObv)
            g.sONOFF = 'on'
            # print('SelObserverON')
    def SelObserverOFF(self):
        try:
            FreeCADGui.Selection.removeObserver(selObv)
            g.sONOFF = 'off'
            # print('SelObserverOFF')
        except Exception as e:
            print('Error2 = ' + str(e))
    def addSelection(self, doc, obj, sub, pnt):  # Selection object
        modmeasure.measureSelected()
        pass
selObv = SelObserver()





toolTipText = \
"""
Selecting one feature will show information about that feature.
Selecting two will show the distance and information of both features.

"""

class MeasureDialog:
    def GetResources(self):
        mypath = os.path.dirname(__file__)
        return {
             'Pixmap': mypath + "/icons/QuickMeasure.svg",
             'MenuText': 'Measure Dialog',
             'ToolTip': toolTipText
             }

    def Activated(self, placeholder = None):
        if FreeCAD.activeDocument() is None:
            mApp('No file is opened.You must open a file first.')
            return
        selObv.SelObserverON() # Checks for part and entity click
        form1.showme('Select one or multiple features to measure')

    def Deactivated(self):
        """This function is executed when the workbench is deactivated."""
        selObv.SelObserverOFF()
        self.IsChecked()

    def IsEnabled(self):
        return()

    def IsActive(self):
        return(True)
FreeCADGui.addCommand('MeasureDialog', MeasureDialog())
#==============================================================================

class mApp(QtGui.QWidget):
    """This message box was added to make this file a standalone file"""
    # for error messages
    def __init__(self, msg, msgtype ='ok'):
        super().__init__()
        self.title = 'Warning'
        self.initUI(msg)

    def initUI(self, msg):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        QtGui.QMessageBox.question(self, 'Warning', msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.Ok)
        self.show()