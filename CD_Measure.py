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
Version.04
"""


import os
import FreeCAD
import FreeCADGui
from PySide import QtGui, QtCore
from PySide.QtGui import *
import math
import numpy
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
        self.fname = 'Empty'
        self.type = 'None'

    def newinfo(self):
        self.area = 0
        self.centerofmass = 0
        self.cylinderlength = ''
        self.bodyname = ''
        self.dia = 0
        self.dia2 = 0
        self.entity = None
        self.fname = ''
        self.type = ''
        self.length = 0 
        self.Name = " No info"
        self.normal = 0
        self.object = None
        self.perimeter = 0
        self.point1 = 0
        self.point2 = 0
        self.radius = 0
        self.radius2 = 0
        self.shape = None
        self.vector = 0
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
        selections = FreeCADGui.Selection.getSelectionEx('', 0)
        selectionslen = len(selections)
        if selectionslen == 0:
            return()

        featsInf0 = len(selections[0].SubElementNames)
        features0 = selections[0].Object.Shape
        f0.newinfo()
        f1.newinfo()
        g.header = ''
        g.msg = ''

        if selectionslen == 1 and featsInf0 == 0:
            ''' If 1 selection but no features are selected then a is body selected.
             Mesure body'''
            name = selections[0].Object.Label
            totarea = self.convertArea(features0.Area)
            totVolume = self.convertVolume(features0.Volume)
            g.header = '{} Body'.format(name)
            g.msg = f'Area = {totarea}\nVolume = {totVolume}'
            form1.txtboxReport.setText(g.msg + '\n' + g.header)
            return()

        numoffeats = 0
        for obj in selections: # Find number of selected surfaces
            numoffeats = numoffeats + len(obj.SubElementNames)
        if len(selections[0].SubElementNames) == 0:
            g.msg = 'Cannot measure feature to body'
        elif numoffeats > 2: # More than 2 features selected
            self.check2plus(selections, selectionslen)
        else:
            #At least 1 feature is selected so fill feature f0 with infomation
            f0.bodyname = selections[0].Object.Label
            f0.fname = selections[0].SubElementNames[0]
            f0.entity = selections[0].Object.getSubObject(f0.fname)
            f0.shape = selections[0].Object.Shape
            f0.object = selections[0].Object
            if "Origin" in f0.fname:
                msg = 'Origin cannot be used for measurements.\n'
                msg = msg + 'Instead: Create a vertex at xyz0 using the\n'
                msg = msg + 'Origin button and use that for measurements.'
                form1.txtboxReport.setText(msg)
                return()
            if f0.entity.ShapeType == 'Vertex':self.getvertex(f0)
            if f0.entity.ShapeType == "Face":self.getface(f0)
            if f0.entity.ShapeType == "Edge":self.getedge(f0)
            
            if selectionslen == 1 and featsInf0 == 1:
                ''' If 1 feature is selected then measure feature.'''
                if 'Vertex' in f0.fname:
                    g.msg = 'x = {}\ny = {}\nz = {}'.format(f0.x, f0.y, f0.z)
                if 'Face' in f0.fname:
                    if 'Sphere' in f0.type:
                        g.msg = ' Sphere Radius = {}\nCenter\nx = {}\ny = {}\nz = {}'.format(f0.radius, f0.x ,f0.y ,f0.z)
                    if 'Cylinder' in f0.type:
                        g.msg =f'Cylinder\nDiameter = {f0.dia}\nRadius = {f0.radius}'
                        if len(str(f0.cylinderlength)) != 0:
                            g.msg = g.msg + '\nLength = ' + str(f0.cylinderlength)
                    if 'Cone' in f0.type:
                        g.msg =f'Cone\nEnd1\nRadius = {f0.radius}\nDiameter = {f0.dia}\nEnd2\nRadius = {f0.radius2}\nDiameter = {f0.dia2}' 
                        if len(str(f0.cylinderlength)) != 0:
                            g.msg = g.msg + '\nLength = ' + str(f0.cylinderlength)
                    if 'Plane' in f0.type:
                        g.msg = 'Plane'
                        if 'Round' in f0.type:
                            if f0.radius2 == 0:
                                g.msg = g.msg +'Round\nCenter of round plane is at: \nx = {}\ny = {}\nz = {}'.format(f0.x, f0.y, f0.z)
                            if f0.radius2 != 0:
                                g.msg = g.msg + f'Bore\nx = {f0.x}\ny = {f0.y}\nz = {f0.z}\nDia 1 = {f0.dia}\Dia 2 = {f0.dia2}'
                    if 'Toroid' in f0.type:
                        g.msg = f0.radius
                    ''' Area added for all surfaces. '''
                    area = self.convertArea(f0.area)
                    g.msg = g.msg + '\nArea = {}\nFace Info'.format(area)
                if 'Edge' in f0.fname:
                    if 'Line' in f0.type:
                        length = self.convertLen(f0.length)
                        g.msg = 'Length = {}\nMid point of line\nx = {}\ny = {}\nz = {}'.format(length, f0.x, f0.y, f0.z)
                    if 'Circle' in f0.type: 
                        circ = self.convertLen(f0.length)
                        g.msg = f'Radius = {f0.radius}\nDia = {f0.dia}\nEdge Length = {circ}\nCenter of Arc is:\nx = {f0.x}\ny = {f0.y}\nz = {f0.z}'
                    if 'Spline' in f0.type or 'Ellipse' in f0.type:
                        shape = FreeCADGui.Selection.getSelectionEx()[0].Object.Shape
                        faces = shape.ancestorsOfType(f0.entity, Part.Face)
                        radii = []
                        for face in faces:
                            surf = face.Surface
                            if hasattr(surf, "Radius"):
                                radii.append(surf.Radius)
                        lmsg = 'Connecting radii'
                        for num in range(len(radii)):
                            lmsg = lmsg + f'\nRad {num} = {self.convertLen(radii[num])}  dia = {self.convertLen(radii[num]*2)}'
                        lmsg = lmsg +'\n'
                        if 'Ellipse' in f0.type:
                            g.msg = 'Ellipse\n' + lmsg
                        else:
                            g.msg = 'Spine\n' + lmsg
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
                    f1.object = selections[0].Object
                else: # If the features are in a (different bodys) get f1.
                    f1.fname = selections[1].SubElementNames[0]
                    f1.shape = selections[1].Object.Shape
                    f1.entity = selections[1].Object.getSubObject(f1.fname)
                    f1.object = selections[1].Object
                # Get information for second feature
                if "Origin" in f0.fname:
                    msg = 'Origin cannot be used for measurements.\n'
                    msg = msg + 'Instead: Create a vertex at xyz0 using the\n'
                    msg = msg + 'Origin button and use that for measurements.'
                    form1.txtboxReport.setText(msg)
                    return()
                feattypes = f0.type + f1.type
                if not 'Toroid' in feattypes: # Toroid cannot be measured to.

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
        if g.msg == '':
            g.msg = 'Cannot calculate between selections'
        form1.txtboxReport.setText(g.msg + '\n' + g.header)
            #end of program


    def checkVertexes(self):
        # Check Vertexes
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
                g.msg = 'Distance = ' + self.convertLen(dist2)
        if 'Face' in featnames:
            if "Sphere" in feattypes:
                g.header = 'Vertex to Sphere center'
                g.msg = self.getMsgBetween()
            if 'Round' in feattypes:
                g.header = 'Vertex to surface center'
                g.msg = self.getMsgBetween()
            if 'Cylinder' in feattypes or 'Cone' in feattypes:
                if 'Vertex' in f0.fname:
                    dist = f0.xyz.distanceToLine(f1.xyz, f1.vector)
                else:
                    dist = f1.xyz.distanceToLine(f0.xyz, f0.vector)
                dist = self.convertLen(dist)
                g.msg = f'Distance = {dist}'
                g.header = 'CenterLine to Vertex'
            if 'Plane' in feattypes:
                p2vDist = self.getvertexToPlane()
                g.header = 'Plane to vertex'
                g.msg = 'Distance = ' + self.convertLen(p2vDist)


    def checkEdges(self):
        # Check edges
        #g.header = 'For test checking edges'
        if 'Edge' in f0.fname and 'Edge' in f1.fname:
            if 'Line' in str(f0.type) and 'Line' in str(f1.type):
                g.header = f0.fname + ' and ' + f1.fname
                dist, parallel = self.findDistBetweenLines(f0.vector, f1.vector, f0.point1, f1.point1)
                ''' Find angle of lines '''
                degstr, angle = self.findanglebetweenlines(f0.vector, f1.vector)
                diststr = self.convertLen(dist)
                if parallel:
                    g.msg = g.msg + 'Lines are parallel\nDist between lines = {}'.format(diststr)
                else:
                    g.msg = 'Angle = {}'.format(degstr)
                    g.msg = g.msg + "\nNot parallel.\nClosest distance is\n{}".format(diststr)
            if 'Circle' in str(f0.type) and 'Circle' in str(f1.type):
                g.header = 'Edge Center to Edge Center'
                g.msg = self.getMsgBetween()
            feattypes = f0.type + f1.type
            if 'Line' in feattypes:
                dist = self.findClosestPointToLine()
                if 'Circle' in feattypes:
                    g.msg = f'Closest arc center to Line\n{dist}\nCenter to midLine' + self.getMsgBetween()
            totlen = self.convertLen(f0.length + f1.length)
            g.msg = g.msg + '\nTotal Length = ' + totlen

        #Find edge and other
        featnames = f0.fname + f1.fname
        feattypes = f0.type + f1.type

        if 'Face' in featnames:
            if 'Sphere' in feattypes:
                if 'Line' in feattypes:
                    g.header = 'Mid Line to Sphere Center'
                    g.msg = self.getMsgBetween()
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
                p2vDist = self.getvertexToPlane()
                g.header = 'Center of Circle Edge to Plane'
                g.msg = 'Distance = ' + self.convertLen(p2vDist)
            if 'Line' in feattypes and 'Cylinder' in feattypes or 'Cone' in feattypes:
                g.header = "Line to CenterLine" 
                dist = 0
                degstr = 0
                dist, parallel = self.findDistBetweenLines(f0.vector, f1.vector,f0.point1,f1.point1)
                degstr, angle = self.findanglebetweenlines(f0.vector, f1.vector)
                dist = self.convertLen(dist)
                
                if parallel:
                  g.msg = f'Line and Centerline are parallel\nClosest dist = {dist}'
                else:
                    g.header = 'Line to CenterLine'
                    g.msg = f'Line and Centerline are not parallel\nClosest dist = {dist}\nAngle = {degstr}'

            if 'Line' in feattypes and 'Plane' in feattypes:
                ang = math.degrees(f0.vector.getAngle(f1.vector))                
                comang = abs(90-ang)
                degstr = self.convertAngle(comang)
                if comang == 0:
                    dist = 0                    
                    diststr = self.findPlaneToLineDistance()
                    g.msg = 'Line is parallel to plane\nDistance = {diststr}'
                else:
                    g.msg = f'Line is not parralllel to plane\nDegrees = {degstr}'
                g.header = 'Degrees beetween plane and line'                
         #End of edges

    def checkSurfaces(self):
        #Report surfaces
        if 'Face' in f0.fname and 'Face' in f1.fname:
            if 'Plane' in f0.type and'Plane' in f1.type:
                myangle = math.degrees( f0.normal.getAngle( f1.normal))
                anglestring = self.convertAngle(myangle)
                g.header = f0.fname + ' and ' + f1.fname
                if myangle == 90 or myangle == 270:
                    g.msg = 'Planes are Normal ' + anglestring
                elif myangle == 0 or myangle == 180:
                    
                    d = f0.entity.Surface.projectPoint(f1.entity.valueAt(0, 0), 'Distance')
                    d = f0.xyz.distanceToPlane(f1.xyz, f1.normal)
                    dists = self.convertLen(d)
                    g.msg = 'Planes are Parallel\nDist = ' + dists
                else:
                    g.msg = "angle between faces = " + anglestring

                if 'Round' in str(f0.type) and 'Round' in str(f1.type):
                    g.header = 'Center to Center'
                    g.msg = g.msg + self.getMsgBetween()
            if 'Sphere' in f0.type and'Sphere' in f1.type:
                g.header = 'Sphere center to Sphere center'
                g.msg = self.getMsgBetween()

            feattypes = f0.type + f1.type
            if 'Cylinder' in f0.type and 'Cylinder' in f1.type or 'Cone' in f0.type or 'Cone' in f1.type:
                if not 'Plane' in feattypes:                   
                    g.header = 'Center Line to Center Line'
                    ''' Find angle of between centerlines. '''
                    parallel = False
                    dist = 0      
                    dist, parallel = self.findDistBetweenLines(f0.vector, f1.vector, f0.point1, f1.point1)
                    diststr = self.convertLen(dist)
                    if dist == 0:
                        g.msg = 'Cannot measure because\none of the cylinders ends in spline'                    
                    else:
                        if parallel:
                            g.msg = 'Features are parallel\nDist between = ' + diststr
                        else:
                            degstr, angle = self.findanglebetweenlines(f0.vector,f1.vector)
                            g.msg = 'Features are not parallel\nAngle = {}\nClosest dist between CL = {}'.format(degstr, diststr)
            
            if 'Sphere' in feattypes and 'Round' in feattypes:
                g.header = 'Sphere center to round face center'
                g.msg = self.getMsgBetween()
            if "Plane" in feattypes and 'Sphere' in feattypes:
                p2vDist = self.getvertexToPlane()
                g.header = 'Center of Sphere to Plane'
                g.msg = 'Distance = ' + self.convertLen(p2vDist)
            if 'Plane' in feattypes and 'Cylinder' in feattypes or 'Plane' in feattypes and 'Cone' in feattypes:
                p2vDist = ''
                ang = math.degrees(f0.vector.getAngle(f1.vector))
                comang = abs(90-ang)
                diststr = self.findPlaneToLineDistance()
                if round(comang,10) == 0:
                    g.msg = f'Centerline and plane is parallel\nDist = {diststr}'
                else:
                    g.msg = f'Centerline and plane are not parallel\nAngle = {round(ang, 10)}\nDistance = {diststr}'
            area = self.convertArea(f0.area + f1.area)
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
            myArea = self.convertArea(totarea)
            g.header = 'Total of {} Faces'.format(numoffeats)
            g.msg = 'Total Area = {}'.format(myArea)
        if alledges:
            myLength = self.convertLen(totlen)
            g.header = 'Total Length of {} Edges'.format(numoffeats)
            g.msg = 'Length = ' + myLength
        ''' End of over 2 selects '''

    def getMsgBetween(self):
        # Finds distant and x y z, then returns results in a string
        x, y, z, d = self.findpointsdistance(f0.xyz, f1.xyz)
        x = self.convertLen(x)
        y = self.convertLen(y)
        z = self.convertLen(z)
        dist = self.convertLen(d)
        lmsg = f"Distance = {dist}\nx = {x}\ny = {y}\nz = {z}"
        return(lmsg)


 
    def getvertexToPlane(self):
        # This sub is from plne to a point. Any xyz.
        if 'Plane' in f0.type:
            print(f0.entity.Vertexes[0].Point)
            print(f0.vector)
            distance = f1.xyz.distanceToPlane(f0.entity.Vertexes[0].Point, f0.vector)
        else:
            distance = f0.xyz.distanceToPlane(f1.entity.Vertexes[0].Point, f1.vector)
        return(distance)
        #plane = Part.Plane(planeloc, normAt) #This line and next is to show plane while testing
        #Part.show(plane.toShape(),"Plane")

    def findPlaneToLineDistance(self):
        dist = 0
        if 'Plane' in f1.type:
            dist = f0.xyz.distanceToPlane(f1.xyz, f1.vector)
        else:
            dist = f1.xyz.distanceToPlane(f0.xyz, f0.vector)                    
        diststr = self.convertLen(dist)
        return(diststr)

    def findClosestPointToLine(self):
        if 'Line' in f0.type:
            direction = f0.entity.Curve.Direction
            dist = f1.xyz.distanceToLine(f0.xyz, direction)
        else:
            direction = f1.entity.Curve.Direction
            dist = f0.xyz.distanceToLine(f1.xyz, direction)
        return(self.convertLen(dist))

    def findDistBetweenLines(self, line1Vector, line2Vector, pointOnLine1, pointOnLine2):
        distoline = 0
        parallel = False
        if pointOnLine1 == 0:
            return([distoline, parallel])
        if pointOnLine2 == 0:
            return([distoline, parallel])
        if line1Vector.isEqual(line2Vector, 1e-12) or line1Vector.isEqual(-line2Vector, 1e-12):
            distoline = pointOnLine1.distanceToLine(pointOnLine2, line2Vector)
            parallel = True
        else: # treat as skew
            n = line1Vector.cross(line2Vector).normalize()
            distoline = abs((pointOnLine1 - pointOnLine2).dot(n))
        return([distoline, parallel])

    def findanglebetweenlines(self, line1Vector, line2Vector):
        angle = line1Vector.getAngle(line2Vector) # In radians
        deg = math.degrees(angle)
        degstring = self.convertAngle(deg)
        return([degstring, angle])




    def getface(self, ci): # ci is for class.info
        face = ci.entity
        ci.type = str(face.Surface)
        if len(face.Edges) == 1:
            ''' Round surfaces '''
            if 'Spline' in str(face.Edges[0].Curve):
                g.msg = 'The edge is a spline'
            else:
                ci.xyz = face.CenterOfMass
                self.getvector(ci.xyz,ci)
                ci.type = 'RoundPlane'
                ci.vector = ci.entity.Surface.Axis
        ci.normal = face.normalAt(0, 0)
        ci.area = face.Area
        if "Plane" in ci.type and ci.xyz == 'n':
            ci.xyz = ci.entity.CenterOfMass
            ci.vector = ci.entity.Surface.Axis
        if 'Cylinder' in ci.type or 'Cone' in ci.type:
            ''' Find two centers in cylinders'''
            edgetypes2 = ''
            ci.vector = ci.entity.Surface.Axis
            for e in face.Edges:
                rstr = str(e.Curve)
                if 'Radius' in rstr:
                    if ci.point1 == 0:
                        #Get first Radius
                        ci.point1 = e.Curve.Center
                        ci.radius = self.convertLen(e.Curve.Radius)[0]
                        ci.dia = self.convertLen(2 * e.Curve.Radius)
                    if ci.point1 != 0 and e.Curve.Center != ci.point1:
                        # Get second radius
                        ci.radius2 = self.convertLen(e.Curve.Radius)
                        ci.dia2 = self.convertLen(2 * e.Curve.Radius)
                        ci.point2 = e.Curve.Center
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
                    ci.cylinderlength = self.convertLen(dis)
            ci.radius = self.convertLen(ci.entity.Surface.Radius)
            ci.xyz = ci.entity.Surface.Center
            self.getvector(ci.entity.Surface.Center, ci)
        if 'Sphere' in ci.type:
            ci.radius = self.convertLen(ci.entity.Surface.Radius)
            ci.xyz = ci.entity.Surface.Center
            self.getvector(ci.entity.Surface.Center, ci)
        if 'Toroid' in ci.type:
            radius1 = self.convertLen(ci.entity.Edges[0].Curve.Radius)
            radius2 = self.convertLen(ci.entity.Edges[1].Curve.Radius)
            lmsg = f'Edge radii\nEdge0 = {radius1}\nEdge1 = {radius2}'
            if len(ci.entity.Edges)>2:
                radius3 = self.convertLen(ci.entity.Edges[2].Curve.Radius)
                lmsg = lmsg + f'\nEdge2 = {radius3}'
            ci.radius = lmsg
        return()

    def getedge(self, ci): #ci = class info
        edge = ci.entity
        ci.length = edge.Length
        ci.type = str(edge.Curve)
        if 'Line' in ci.type:
            ci.xyz = edge.CenterOfMass
            self.getvector(edge.CenterOfMass, ci)
            ci.point1 = edge.Vertexes[0].Point
            ci.point2 = edge.Vertexes[1].Point
            ci.vector = edge.Curve.Direction
        if 'Circle' in ci.type:
            ci.radius = self.convertLen(edge.Curve.Radius)
            ci.dia = self.convertLen(2 * edge.Curve.Radius)
            ci.xyz = edge.Curve.Center
            self.getvector(ci.xyz, ci)
        return()

    def getvertex(self, ci):
        vertex = ci.entity
        ci.type = 'Vertex'
        ci.xyz = vertex.Point
        self.getvector(ci.xyz, ci)
        return(ci)
    
    def getvector(self, vector, ci):
        ci.xyz = vector
        x, y, z = ci.xyz
        ci.x = self.convertLen(x)
        ci.y = self.convertLen(y)
        ci.z = self.convertLen(z)
        return(ci)

    def convertLen(self, length):
        lenstr = FreeCAD.Units.Quantity(length, FreeCAD.Units.Length).UserString
        return(lenstr)

    def convertArea(self, area):
        areastr = FreeCAD.Units.Quantity(area, FreeCAD.Units.Area).UserString
        return(areastr)

    def convertVolume(self, volume):
        volumestr = FreeCAD.Units.Quantity(volume, FreeCAD.Units.Volume).UserString
        return(volumestr)

    def convertAngle(self, angleInDegs):
        anglestr = FreeCAD.Units.Quantity(angleInDegs, FreeCAD.Units.Angle).UserString
        return(anglestr)

    def findpointsdistance(self, arraypoint0, arraypoint1):
        lengx, lengy, lengz = abs(arraypoint0 - arraypoint1)
        ''' Calulate distant between points '''
        distance = math.dist( arraypoint0, arraypoint1)
        return([lengx, lengy, lengz, distance])

modmeasure = measureClass()

class createPoints():

    def ToggleOrigin(self):
        ShowOrg = self.deletepoints(self, 'QM_XYZ0')
        #Show the origion of the part.
        if ShowOrg:
            self.createpoint(self, 'QM_XYZ0', FreeCAD.Vector(0,0,0))

    def midLine(self):
        sels = FreeCADGui.Selection.getSelectionEx('', 0)
        if len(sels) == 0 :
            return()
        featname = sels[0].SubElementNames[0]
        print(featname)
        if 'Edge' in featname:
            entity = sels[0].Object.getSubObject(featname)
            print(entity.Curve)
            if "Line" in str(entity.Curve):
                self.createpoint(self, 'QM_Mid',entity.CenterOfMass)

            if 'Radius' in str(entity.Curve):
                print(entity.Curve.Center)
                self.createpoint(self, 'QM_Circle Center',entity.Curve.Center)

    def deletepoints(self, pname):
        print(pname)
        found = True
        for obj in FreeCAD.ActiveDocument.Objects:
            if pname in obj.Label:
                FreeCAD.ActiveDocument.removeObject(obj.Name)
                found = False
        return(found)

    def createpoint(self, pname, vector):
        FreeCADGui.Selection.clearSelection()
        point = Part.Vertex(vector)
        Point = Part.show(point, pname)
        Point.ViewObject.PointSize = 10
        Point.ViewObject.PointColor = (55.0,0.0,0.0)

class formMain(QtGui.QMainWindow):

    def __init__(self, name):
        self.name = name
        super(formMain, self).__init__()
        self.setWindowTitle('Quick Measure')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(280, 150, 300, 200)
        self.setStyleSheet("font:10pt arial MS")

        self.txtboxReport = QtGui.QTextEdit(self)
        self.txtboxReport.setGeometry(5, 54, 650, 90) # xy, wh

        self.btnclearAll = QtGui.QPushButton(self)
        self.btnclearAll.move(10, 4)
        self.btnclearAll.setFixedWidth(60)
        self.btnclearAll.setFixedHeight(24)
        self.btnclearAll.setToolTip("Clear all")
        self.btnclearAll.setText("Clear")
        self.btnclearAll.clicked.connect(lambda:self.ClearAll())
        self.btnclearAll.setStyleSheet("padding:2px")

        self.btncopytoClipB = QtGui.QPushButton(self)
        self.btncopytoClipB.move(70, 4)
        self.btncopytoClipB.setFixedWidth(60)
        self.btncopytoClipB.setFixedHeight(24)
        self.btncopytoClipB.setToolTip("Copy text to clipboard")
        self.btncopytoClipB.setText("Copy")
        self.btncopytoClipB.clicked.connect(lambda:self.CopyToClipboard())
        self.btncopytoClipB.setStyleSheet("padding:2px")

        self.btnCloseForm = QtGui.QPushButton(self)
        self.btnCloseForm.move(200, 4)
        self.btnCloseForm.setFixedWidth(60)
        self.btnCloseForm.setFixedHeight(24)
        self.btnCloseForm.setToolTip("Close this form.")
        self.btnCloseForm.setText("Close")
        self.btnCloseForm.clicked.connect(lambda:self.closeme())
        self.btnCloseForm.setStyleSheet("padding:2px")

        self.btnToggleOrgin = QtGui.QPushButton(self)
        self.btnToggleOrgin.move(10, 28)
        self.btnToggleOrgin.setFixedWidth(60)
        self.btnToggleOrgin.setFixedHeight(24)
        self.btnToggleOrgin.setToolTip("Toggles an Origin point, on and off,\nwhich can be used for measurements.")
        self.btnToggleOrgin.setText("Origin")
        self.btnToggleOrgin.clicked.connect(lambda:createPoints.ToggleOrigin(createPoints))
        self.btnToggleOrgin.setStyleSheet("padding:2px")

        self.btnMidLine = QtGui.QPushButton(self)
        self.btnMidLine.move(70, 28)
        self.btnMidLine.setFixedWidth(130)
        self.btnMidLine.setFixedHeight(24)
        binfo = '''Select a line, edge or arc then select this button.
A point will be created at the mid point of a the edge or center of the arc.
You can then use the points for measurements.
'''
        self.btnMidLine.setToolTip(binfo)
        #self.btnMidLine.setToolTip("Creates a point at the middle of a straight lineor arc,\nwhich can\nbe used for measurements.")
        self.btnMidLine.setText("Mid Line, Arc Center")
        self.btnMidLine.clicked.connect(lambda:createPoints.midLine(createPoints))
        self.btnMidLine.setStyleSheet("padding:2px")

        self.btnDeleteMid = QtGui.QPushButton(self)
        self.btnDeleteMid.move(200, 28)
        self.btnDeleteMid.setFixedWidth(95)
        self.btnDeleteMid.setFixedHeight(24)
        self.btnDeleteMid.setToolTip("Deletes all points added to the middle of lines and center of circles.")
        self.btnDeleteMid.setText("Del Mid Points")
        #deletes all points with QM_ in the name
        self.btnDeleteMid.clicked.connect(lambda:createPoints.deletepoints(createPoints, 'QM_'))
        self.btnDeleteMid.setStyleSheet("padding:2px")

    def CopyToClipboard(self):
        memo = QtGui.QApplication.clipboard()
        txt = self.txtboxReport.toPlainText()
        memo.setText(u"{}".format(txt), mode = memo.Clipboard) # store in
        #memo.clear(mode=memo.Clipboard ) # clear clipBoard



    def ClearAll(self):
        form1.txtboxReport.setText('')
        FreeCADGui.Selection.clearSelection()


    def resizeEvent(self, event):
        # resize table
        formx = self.width()
        formy = self.height()
        self.txtboxReport.resize(formx - 20, formy - 20)

    def showme(self, msg):
        self.txtboxReport.setText(msg)
        self.show()
        selObv.SelObserverON
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
    def addSelection(self, doc, obj, sub, pnt): # Selection object
        modmeasure.measureSelected()
    def removeSelection(self, doc, obj, sub): # Delete the selected object
        modmeasure.measureSelected()
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
             'Pixmap': mypath + "/Icons/QuickMeasure.svg",
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

