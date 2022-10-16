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
pre-release .00003
"""


import os
import FreeCAD
import FreeCADGui
from PySide import QtGui, QtCore
from PySide.QtGui import *
import math
import numpy
#import DraftGeomUtils
import Part
import Draft

class globaluseclass:
    def __init__(self, name):
        self.sONOFF = 'off'
        self.msg = ''
        self.header = ''
g = globaluseclass("g")


class info:
    def __init__(self):
        self.area = 0
        self.centerofmass = 0
        self.bodyname = ''
        self.cylinderlength = ''
        self.entity = None
        self.fname = ''
        self.type = '' #Circle or Line
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
        self.cylinderlength = ''
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
        self.radius2 = 0
        self.shape = None
        self.x = 'n'
        self.y = 'n'
        self.z = 'n'
        self.xyz = 'n'


    def __str__(self):
        return f'{self.fname, self.type}'
f0 = info() # Two features are needed so created a class for features 1 and 2
f1 = info()

class measureClass:
    def __init__(self):
        pass
    def measureSelected(self):
        selections = FreeCADGui.Selection.getSelectionEx()
        selectionslen = len(selections)
        if selectionslen == 0:
            return()

        featsInf0 = len(selections[0].SubElementNames)
        features0 = selections[0].Object.Shape
        f0.clear()
        f1.clear()
        g.header = ''
        g.msg = ''
        
        
        if selectionslen == 1 and featsInf0 == 0:
            ''' If 1 selection but no features are selected then a is body selected.
             Mesure body'''
            name = selections[0].Object.Label
            totarea = self.convertArea([features0.Area])[0]
            totVolume = self.convertVolume([features0.Volume])[0]
            g.header = '{} Body'.format(name)
            g.msg = 'Area = {}\nVolume = {}'.format(name, totarea, totVolume)
            form1.txtboxReport.setText(g.msg + '\n' + g.header)
            return()

        numoffeats = 0
   
        for o in selections: # Find number of selected surfaces
            numoffeats = numoffeats + len(o.SubElementNames)
        if numoffeats > 2: # More than 2 features selected
            self.check2plus(selections, selectionslen)
        else:
            #At least 1 feature is selected so fill feature f0 with infomation
            f0.bodyname = selections[0].Object.Label
            f0.fname = selections[0].SubElementNames[0]
            f0.entity = selections[0].Object.getSubObject(f0.fname)
            f0.shape = selections[0].Object.Shape

            if "Vertex" in f0.fname:self.getvertex(f0)
            if "Face" in f0.fname:self.getface(f0)
            if "Edge" in f0.fname:
                self.getedge(f0)
                ''' Next lines are future feature '''
                #midpoint0 = Part.Vertex(f0.xyz)
                #p = Part.show(midpoint0, 'MidPoint1')
                #p.ViewObject.PointSize = 5
            if selectionslen == 1 and featsInf0 == 1:
                ''' If 1 feature is selected then measure feature.'''
                if 'Vertex' in f0.fname:
                    g.msg = 'x = {}\ny = {}\ny = {}'.format(f0.x, f0.y, f0.z)

                if 'Face' in f0.fname:
                    if 'Sphere' in f0.type:
                        g.msg = ' Sphere Radius = {}\nCenter\nx = {}\ny = {}\nz = {}'.format(f0.radius, f0.x ,f0.y ,f0.z)
                    if 'Cylinder' in f0.type:
                        g.msg = 'Cylinder Radius = '+ f0.radius
                        if len(str(f0.cylinderlength)) != 0:
                            g.msg = g.msg + '\nLength = ' + str(f0.cylinderlength)
                    if 'Cone' in f0.type:
                        g.msg = 'Cone\nRadius1 = {}\nRadius2 = {}'.format(f0.radius, f0.radius2)
                        if len(str(f0.cylinderlength)) != 0:
                            g.msg = g.msg + '\nLength = ' + str(f0.cylinderlength)
                    if 'Plane' in f0.type:
                        if 'Round' in f0.type:
                            if f0.radius2 == 0:
                                g.msg = g.msg +'Round\nx = {}\ny = {}\nz = {}'.format(f0.x, f0.y, f0.z)
                            if f0.radius2 != 0:
                                g.msg = g.msg +'Bore\nx = {}\ny = {}\nz = {}\nRadius1 = {}\nRadius2 = {}'.format(f0.x, f0.y, f0.z, f0.radius, f0.radius2)
                    if 'Toroid' in f0.type:
                        g.msg = 'radius = ' + f0.radius
                    ''' Area added for all surfaces. '''
                    area = self.convertArea([f0.area])[0]
                    g.msg = g.msg + '\nArea = {}\nFace Info'.format(area)

                if 'Edge' in f0.fname:
                    if 'Line' in f0.type:
                        length = self.convertLen([f0.length])[0]
                        g.msg = 'Length = {}\nCenter of line\nx = {}\ny = {}\nz = {}'.format(length, f0.x, f0.y, f0.z)
                    if 'Circle' in f0.type: 
                        circ = self.convertLen([f0.length])[0]
                        radius = self.convertLen([f0.radius])[0]
                        g.msg = 'Radius = {}\nEdge Length = {}\nx = {}\ny = {}\nz = {}'.format(radius, circ, f0.x, f0.y, f0.z)

                    if 'Spline' in f0.type:
                        g.msg = 'Spline\nLength = ' + self.convertLen([f0.length])[0]
                if g.msg == '':
                    g.header = '\nI cannot measure that feature'
                else:
                    g.header = '{} of {}'.format(f0.fname, f0.bodyname)
            featsin1 = 0
            if selectionslen == 2:
                #If selection length is 2
                    featsin1 = len(selections[1].SubElementNames) #Check the number of entities in selection 1.

            ''' sort to see if both features are on the same body or two bodies. ''' 
            if selectionslen == 1 and featsInf0 == 2 or selectionslen == 2 and featsInf0 == 1 and featsin1 == 1:
                if selectionslen == 1: # If both features are on the (same body) get f1 feature
                    f1.fname = selections[0].SubElementNames[1]
                    f1.shape = selections[0].Object.Shape
                    f1.entity = selections[0].Object.getSubObject(f1.fname)
                else: # If the features are in a (different bodys) get f1.
                    f1.fname = selections[1].SubElementNames[0]
                    f1.shape = selections[1].Object.Shape
                    f1.entity = selections[1].Object.getSubObject(f1.fname)
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
        if g.header == '':
            g.header = 'Cannot calculate between selections'
        form1.txtboxReport.setText(g.msg + '\n' + g.header)
            #end of program


    def checkVertexes(self):
        # Check Vertexes
        #g.header = 'For test checking vertexes'
        if "Vertex" in f0.fname and 'Vertex' in f1.fname:
            g.header = 'Vertex to Vertex'
            g.msg = self.getMsgBetween()
        featnames = f0.fname + f1.fname
        feattypes = f0.type + f1.type
        if 'Edge' in featnames:
            if 'Circle' in feattypes:
                g.header = 'Vertex to Circle center'
                g.msg = self.getMsgBetween()
            if 'Line' in feattypes:
                dist2 = self.findClosestPointToLine()
                g.header = 'Vertex to infinte Line'
                g.msg = 'Distance = ' + self.convertLen([dist2])[0]
        if 'Face' in featnames:
            if "Sphere" in feattypes:
                g.header = 'Vertex to Sphere center'
                g.msg = self.getMsgBetween()
            if 'Round' in feattypes:
                g.header = 'Vertex to surface center'
                g.msg = self.getMsgBetween()
        if 'Plane' in feattypes:
            p2vDist = ''
            if "Plane" in f0.type:
                p2vDist = self.getvertexToPlane(f0.entity, f1.xyz)
            else:
                p2vDist = self.getvertexToPlane(f1.entity, f0.xyz)
            g.header = 'Plane to vertex'
            g.msg = 'Distance = ' + self.convertLen([p2vDist])[0]


    def checkEdges(self):
        # Check edges
        #g.header = 'For test checking edges'
        if 'Edge' in f0.fname and 'Edge' in f1.fname:
            if 'Line' in str(f0.type) and 'Line' in str(f1.type):
                g.header = f0.fname + ' and ' + f1.fname
                dist, parallel = self.findDistBetweenLines(f0.point1, f0.point2, f1.point1, f1.point2)
                dist = self.convertLen([dist])[0]
                if parallel:
                    dist = self.convertLen([dist])[0]
                    g.msg = g.msg + 'Lines are parallel\nDist between lines = {}'.format(dist)
                else:
                    ''' Find angle of lines. '''
                    degstr, angle = self.findanglebetweenlines(f0.point1, f0.point2, f1.point1, f1.point2)
                    g.msg = 'Angle = {}'.format(degstr)
                    g.msg = g.msg + "\nNot parallel.\nClosest distance is\n{}".format(dist)
            if 'Circle' in str(f0.type) and 'Circle' in str(f1.type):
                g.header = 'Edge Center to Edge Center'
                g.msg = self.getMsgBetween()

            feattypes = f0.type + f1.type
            if 'Line' in feattypes and 'Circle' in feattypes:
                g.header = 'Circle to mid line'
                g.msg = self.getMsgBetween()
            totlen = self.convertLen([f0.length + f1.length])[0]
            g.msg = g.msg + '\nTotal Length = ' + totlen

        #Find edge and other
        featnames = f0.fname + f1.fname
        feattypes = f0.type + f1.type
        if 'Face' in featnames:
            #g.header = 'in Face check'
            if 'Sphere' in feattypes:
                if 'Line' in feattypes:
                    g.header = 'Mid Line to Sphere Center'
                if 'Circle' in feattypes:
                    g.header = 'Curve center to Sphere center'
                g.msg = self.getMsgBetween()
            if 'Round' in feattypes and 'Circle' in feattypes:
                g.msg = self.getMsgBetween()
                g.header = 'Circle Center to Face Center'
            if 'Round' in feattypes and 'Line' in feattypes:
                g.header = 'Mid Line to Face Center'
                g.msg = self.getMsgBetween()
        if "Plane" in feattypes and 'Circle' in feattypes:
                p2vDist = ''
                if 'Plane' in f0.type:
                    p2vDist = self.getvertexToPlane(f0.entity, f1.xyz)
                else:
                    p2vDist = self.getvertexToPlane(f1.entity, f0.xyz)
                g.header = 'Center of Circle Edge to Plane'
                g.msg = 'Distance = ' + self.convertLen([p2vDist])[0]
         #End of edges

    def checkSurfaces(self):
        #Report surfaces
        #g.header = 'For test checking faces'
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

                if 'Round' in str(f0.type) and 'Round' in str(f1.type):
                    g.header = 'Center to Center'
                    g.msg = g.msg + self.getMsgBetween()
            if 'Sphere' in f0.type and'Sphere' in f1.type:
                g.header = 'Sphere center to Sphere center'
                g.msg = self.getMsgBetween()
            if 'Toroid' in f0.type and'Toroid' in f1.type:
                g.header = 'Radius1 and Radius2'
                g.msg = 'Radius1 = {}\nRadius2 = {}'.format( f0.radius, f1.radius)
            if 'Cylinder' in f0.type and 'Cylinder' in f1.type:
                g.header = 'Cylinder to cylinder'
                ''' Find angle of between centerlines. '''
                if f0.point1 == 0 or f0.point2 == 0:
                    g.msg = 'No Angle because:\nFirst Cylinder ends in a spline'
                elif f1.point1 == 0 or f1.point2 == 0:
                    g.msg = 'No angle because:\nSecond Cylinder ends in a spline'
                else:
                    dist, parallel = self.findDistBetweenLines(f0.point1, f0.point2, f1.point1, f1.point2)
                    dist = self.convertLen([dist])[0]
                    if parallel:
                        g.msg = 'Cylinders are parallel\nDist between = ' + dist
                    else:
                        degstr, angle = self.findanglebetweenlines(f0.point2, f0.point1, f1.point1, f1.point2)
                        g.msg = 'Cylinders are not parrallel\nAngle = {}\nClosest dist between CL = {}'.format(degstr, dist)
                g.msg = g.msg + '\nRadius1 = {}\nRadius2 = {}'.format( f0.radius, f1.radius)
            feattypes = f0.type + f1.type
            if 'Sphere' in feattypes and 'Round' in feattypes:
                g.header = 'Sphere center to round face center'
                g.msg = self.getMsgBetween()
            if "Plane" in feattypes and 'Sphere' in feattypes:
                p2vDist = ''
                if 'Plane' in f0.type:
                    p2vDist = self.getvertexToPlane(f0.entity, f1.xyz)
                else:
                    p2vDist = self.getvertexToPlane(f1.entity, f0.yxz)
                g.header = 'Center of Sphere to Plane'
                g.msg = 'Distance = ' + self.convertLen([p2vDist])[0]
            area = self.convertArea([f0.area + f1.area])[0]
            #perimeter = self.convertLen([f0.perimeter + f1.perimeter])[0]
            g.msg = g.msg + '\nTotal Area = {}'.format(area)

    def check2plus(self, selections, selectionslen):
        # check when selections are 3 or more
        numoffeats = 0
        for o in selections:
            numoffeats = numoffeats + len(o.SubElementNames)
        allfaces = True
        alledges = True
        totlen = 0
        totarea = 0
        for sel in selections:
            for featname in sel.SubElementNames:
                subobject = sel.Object.getSubObject(featname)
                if 'Face' in featname:
                    totarea = totarea + subobject.Area
                    alledges = False
                if 'Edge' in featname:
                    totlen = totlen + subobject.Length
                    allfaces = False
                if 'Vertex' in featname:
                    alledges = False
                    allfaces= False
        if allfaces:
            myArea = self.convertArea([totarea])[0]
            g.header = 'Total of {} Faces'.format(numoffeats)
            g.msg = 'Total Area = {}'.format(myArea)
        if alledges:
            myLength = self.convertLen([totlen])[0]
            g.header = 'Total Length of {} Edges'.format(numoffeats)
            g.msg = 'Length = ' + myLength

    def getMsgBetween(self):
        # Finds distant and x y z, then returns results in a string
        xyzd = self.findpointsdistance(f0.xyz, f1.xyz)
        x, y, z, dist = self.convertLen(xyzd)
        lmsg = "Distance = {}\nx = {}\ny = {}\nz = {}".format(dist, x, y, z)
        return(lmsg)
    
    def getvertexToPlane(self,planefeat,measureFromVector):
        # measure from vextor is xyz vector,Sphere etc. 
        normAt = planefeat.normalAt(0, 0) # normal to plane vector
        planeloc = planefeat.Vertexes[0].Point #Location of plane
        #plane = Part.Plane(planeloc, normAt) #This line and next is to show plane while testing
        #Part.show(plane.toShape(),"Plane")
        distance = measureFromVector.distanceToPlane(planeloc, normAt)
        return(distance)
    
    def findClosestPointToLine(self):
        if 'Line' in f0.type:
            direction = f0.entity.Curve.Direction
            dist = f1.xyz.distanceToLine(f0.xyz, direction)
        else:
            direction = f1.entity.Curve.Direction
            dist = f0.xyz.distanceToLine(f1.xyz, direction)
        return(dist)

    def findDistBetweenLines(self, line1p1, line1p2, line2p1, line2p2):
        distoline = 0
        parallel = False
        line1 = Part.makeLine(line1p1, line1p2)
        line2 = Part.makeLine(line2p1, line2p2)
        dir1 = line1.Curve.Direction
        dir2 = line2.Curve.Direction
        if dir1.isEqual(dir2, 1e-12) or dir1.isEqual(-dir2, 1e-12):
            distoline = line1p1.distanceToLine(line2p1, dir1)
            parallel = True
        else: # treat as skew
            n = dir1.cross(dir2).normalize()
            distoline = abs((line2p1 - line1p1).dot(n))
        return([distoline, parallel])

    def findanglebetweenlines(self, line0vertex1, l0v2, l1v1, l1v2):
        vec1 = line0vertex1 - l0v2
        vec2 = l1v2 - l1v1
        angle = vec1.getAngle(vec2) # In radians
        deg = math.degrees(angle)
        degstring = self.convertAngle([deg])[0]
        return([degstring, angle])

    def getface(self, ci): # ci is for class.info
        face = ci.entity
        ci.type = str(face.Surface)
        if len(face.Edges) == 1:
            ''' Round surfaces '''
            ci.xyz = face.CenterOfMass
            ci.x, ci.y, ci.z = self.convertLen(ci.xyz)
            ci.type = 'RoundPlane'
        if len(face.Edges) == 2:
            ''' Counterbore type '''
            ci.xyz = face.CenterOfMass
            ci.x, ci.y, ci.z = self.convertLen(ci.xyz)
            ci.type = 'RoundPlane'
            ci.radius = self.convertLen([face.Edges[0].Curve.Radius])[0]
            ci.radius2 = self.convertLen([face.Edges[1].Curve.Radius])[0]
        ci.normal = face.normalAt(0, 0)
        ci.area = face.Area
        if 'Cylinder' in ci.type or 'Cone' in ci.type:
            ''' Find two centers in cylinders'''
            edgetypes2 = ''
            for e in face.Edges:
                rstr = str(e.Curve)
                if 'Radius' in rstr:
                    if ci.point1 == 0:
                        ci.point1 = e.Curve.Center
                        ci.radius = self.convertLen([e.Curve.Radius])[0]
                    if ci.point1 != 0 and e.Curve.Center != ci.point1:
                        ci.point2 = e.Curve.Center
                        ci.radius2 = self.convertLen([e.Curve.Radius])[0]
                else:
                    edgetypes2 = edgetypes2 + rstr
            ''' If the end of a cylinder is s spline, report it as spline '''
            if ci.point1 == 0 or ci.point2 == 0:
                if 'Spline' in edgetypes2 or 'Sphere' in edgetypes2:
                    ci.cylinderlength = 'Cylinder ends in spline'
                pass
            else:
                dis = self.findpointsdistance(ci.point1, ci.point2)[3]
                if dis != 0:
                    ci.cylinderlength = self.convertLen([dis])[0]
            #ci.radius = self.convertLen([ci.entity.Surface.Radius])[0]
            self.getvector(ci.entity.Surface.Center, ci)
        if 'Sphere' in ci.type:
            ci.radius = self.convertLen([ci.entity.Surface.Radius])[0]
            self.getvector(ci.entity.Surface.Center, ci)
        if 'Toroid' in ci.type:
            ci.radius = self.convertLen([ci.entity.Edges[0].Curve.Radius])[0]
        return()

    def getedge(self, ci): #ci = class info
        edge = ci.entity
        ci.length = edge.Length
        ci.type = str(edge.Curve)
        if 'Line' in ci.type:
            self.getvector(edge.CenterOfMass, ci)
            ci.point1 = edge.Vertexes[0].Point
            ci.point2 = edge.Vertexes[1].Point
        if 'Circle' in ci.type:
            ci.radius = edge.Curve.Radius
            ci.xyz = edge.Curve.Center
            self.getvector(edge.Curve.Center, ci)
        return()

    def getvertex(self, ci):
        vertex = ci.entity
        ci.type = 'Vertex'
        self.getvector(vertex.Point, ci)
        return(ci)
    
    def getvector(self, vector, ci):
        ci.xyz = vector
        ci.x, ci.y, ci.z = self.convertLen(vector)
        return(ci)

    def convertLen(self, listofvalues):
        anslist = []
        for e in listofvalues:
            if 'str' in str(type(e)):
                string = e
            else:
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

    def findpointsdistance(self, arraypoint0, arraypoint1):
        lengx, lengy, lengz = abs(arraypoint0 - arraypoint1)
        ''' Calulate distant between points '''
        distance = math.dist( arraypoint0, arraypoint1)
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
        #if len(FreeCADGui.Selection.getSelectionEx()) > 0:
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

class QuickMeasure:
    def GetResources(self):
        mypath = os.path.dirname(__file__)
        return {
             'Pixmap': mypath + "/icons/QuickMeasure.svg",
             'MenuText': 'Quick Measure',
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
        print('Deactivated')
        #self.IsChecked()

    def IsEnabled(self):
        return()

    def IsActive(self):
        return(True)
FreeCADGui.addCommand('QuickMeasureTool', QuickMeasure())
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

