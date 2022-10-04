# -*- coding: utf-8 -*-
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2022 Dan Miel                                           *
#*                                                                         *
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

''' 
Quick Measure program
written by Dan Miel
'''

import FreeCAD
import FreeCADGui
import os
import QM_dict
#print('************************************')
#mypath = os.path.dirname(__file__)
#print(mypath + '===========================')

import sys
PyVersion = sys.version_info[0]
if PyVersion == 2:
    import a2p_Resources2
else:
    import a2p_Resources3


class QuickMeasure (Workbench):

    def __init__(self):
        import QM_dict
        mypath = QM_dict.getdir(None)
        self.__class__.Icon = mypath + "/icons/QuickMeasure.svg"
        self.__class__.MenuText = 'MeasureDialog'

    def Initialize(self):
        FreeCADGui.updateLocale()
        import CD_Measure


        DiagnosticCommands = [
            'MeasureDialog'
           
            ]
       
        self.appendToolbar(
           'MeasureBar',
           DiagnosticCommands
           )

    def Activated(self):
        pass

    def Deactivated(self):
        pass

    def ContextMenu(self, recipient):
        import FreeCAD, FreeCADGui

        self.appendContextMenu(
            "Measure Dialog",
            [                      
                'MeasureDialog'
                ]
            )

Gui.addWorkbench(QuickMeasure())
