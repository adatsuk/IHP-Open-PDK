########################################################################
#
# Copyright 2024 IHP PDK Authors
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
########################################################################
__version__ = '$Revision: #3 $'

from cni.dlo import *
from geometry import *
from utility_functions import *

import math

class sealring(DloGen):

    @classmethod
    def defineParamSpecs(cls, specs):   
        techparams = specs.tech.getTechParams()
        
        CDFVersion = techparams['CDFVersion']
        
        specs('cdf_version', CDFVersion, 'CDF Version')
        specs('Display', 'Selected', 'Display', ChoiceConstraint(['All', 'Selected']))
             
        specs('l', '150u', 'Length(X-Axis)')
        specs('w', '150u', 'Width(Y-Axis)')
        specs('wfill', '30u', 'Filler ring width')
        specs('addLabel', 'nil', 'Add sub! label', ChoiceConstraint(['nil', 't']))
        specs('addSlit', 'nil' , 'Add Slit', ChoiceConstraint(['nil', 't']))
        
        specs('Lmin', '150u', 'Lmin')
        specs('Wmin', '150u', 'Wmin')

    def setupParams(self, params):
        # process parameter values entered by user
        self.params = params
        self.l = params['l']
        self.w = params['w']
        self.wfill = params['wfill']
        self.addLabel = params['addLabel']
        self.addSlit = params['addSlit']

    def genLayout(self):
        techparams = self.tech.getTechParams()
        self.techparams = techparams
        self.epsilon = techparams['epsilon1']
        
        l = self.l
        w = self.w
        wfill = self.wfill
        addLabel = self.addLabel
        addSlit = self.addSlit

        corneroffset = self.techparams['Seal_k']
        cont_size = self.techparams['Cnt_a']
        vian_size = self.techparams['Vn_a']
        TV1_size = self.techparams['TV1_a']
        TV2_size = self.techparams['TV2_a']
        
        # PCell Code
        
        w = Numeric(w)*1e6;
        l = Numeric(l)*1e6;
        wfill = Numeric(wfill)*1e6;
        
        maxMetalWidth = 4.2
        maxMetalLength = maxMetalWidth * 2
        corner_width = 4.2
        metalOffset = 3 + corner_width
        viaOffset = 5.1 + corner_width
        corner_length = corner_width * 2
        corner_starty = 0   # start at the bottom right
        corner_steps = 4
        corner_end = 28.2   # end of the bottom right and top left
        corner_startx = corner_end - (corner_end - corner_width * (corner_steps + 1))
        metal_startx = corner_end - (corner_end - maxMetalWidth * (corner_steps + 1)) + metalOffset
        
        # Sealring Corner
        layers = ['Activ', 'pSD', 'EdgeSeal', 'Metal1', 'Metal2', 'Metal3', 'Metal4', 'Metal5', 'TopMetal1', 'TopMetal2']
        vias = ['Cont', 'Via1', 'Via2', 'Via3', 'Via4', 'TopVia1', 'TopVia2']
        
        item_list = list()
        groupId   = list()
        
        # Passiv
        layerobj = dbCreateRect(self, Layer('Passiv', 'drawing'), Box(corner_startx, corner_starty, corner_end, corner_width))
        item_list.append(layerobj)
        layerobj = generateCorner(self, corner_startx, corner_starty, corner_width, corner_length, corner_steps, corner_end, 0, 'Passiv')
        item_list += layerobj
        groupId = combineLayerAndDelete(self, item_list, groupId, 'Passiv')
        
        item_list = []
        
        # Metals
        for layer in layers :
            layerobj = generateCorner(self, metal_startx, corner_starty, maxMetalWidth, maxMetalLength, corner_steps, corner_end, metalOffset, layer)
            groupId = combineLayerAndDelete(self, layerobj, groupId, layer)
           
        # Vias
        for layer in vias :
            if layer == 'TopVia1' :
                viaWidth = TV1_size
                viaLength = 4.2
            elif layer == 'TopVia2' :
                viaWidth = TV2_size
                viaLength = 4.2
            elif layer == 'Cont' :
                viaWidth = cont_size
                viaLength = 4.2
            else :
                viaWidth = vian_size
                viaLength = 4.2

            via_startx = corner_end - (corner_end - maxMetalWidth * (corner_steps + 1)) + metalOffset - maxMetalWidth/2-0.1
            layerobj = dbCreateRect(self, layer, Box(via_startx, viaOffset, via_startx+viaWidth, viaOffset+viaLength))
            cons(item_list, layerobj)
            
            viaGroupId = layerobj
            
            for cnt in range(1, corner_steps+1) :
                layerobj = dbCopyShape(viaGroupId, Point(2 * viaOffset + viaLength * cnt + viaWidth-0.1, -viaLength*(cnt-1)), 'R90')
                cons(item_list, layerobj)
                layerobj = dbCopyShape(viaGroupId, Point(-maxMetalWidth*(cnt-1), maxMetalWidth*(cnt-1)-0.1), 'R0')
                cons(item_list, layerobj)

            layerobj = dbCreateRect(self, layer, Box(via_startx, viaOffset-0.1, corner_end, viaOffset-0.1+viaWidth))
            cons(item_list, layerobj)
            layerobj = dbCreateRect(self, layer, Box(viaOffset-0.1, corner_end -  maxMetalWidth/2-0.1, viaOffset-0.1+viaWidth, corner_end))
            cons(item_list, layerobj)
            groupId = combineLayerAndDelete(self, item_list, groupId, layer)
            
            item_list = []

        # Copy Corners
        ihpCopyFig(groupId, Point(l, w), 'R180')
        ihpCopyFig(groupId, Point(l, 0), 'R90')
        ihpCopyFig(groupId, Point(0, w), 'R270')
        
        # end PCell Code

        # Straight Lines
        dbCreateRect(self, Layer('Passiv', 'drawing'), Box(0.0, corner_end, corner_width, w - corner_end))
        dbCreateRect(self, Layer('Passiv', 'drawing'), Box(corner_end, 0.0, l - corner_end, corner_width))
        dbCreateRect(self, Layer('Passiv', 'drawing'), Box(l, corner_end, l - corner_width, w - corner_end))
        dbCreateRect(self, Layer('Passiv', 'drawing'), Box(corner_end, w, l - corner_end, w - corner_width))
       
        for layer in layers :
            dbCreateRect(self, Layer(layer, 'drawing'), Box(metalOffset, corner_end, metalOffset + corner_width, w - corner_end))
            dbCreateRect(self, Layer(layer, 'drawing'), Box(corner_end, metalOffset, l - corner_end, metalOffset + corner_width))
            dbCreateRect(self, Layer(layer, 'drawing'), Box(l - metalOffset, corner_end, l - corner_width - metalOffset, w - corner_end))
            dbCreateRect(self, Layer(layer, 'drawing'), Box(corner_end, w - metalOffset, l - corner_end, w - corner_width - metalOffset))
            
        for layer in vias :
            if layer == 'TopVia1' :
                viaWidth = TV1_size
                viaLength = 4.2
            elif layer == 'TopVia2' :
                viaWidth = TV2_size
                viaLength = 4.2
            elif layer == 'Cont' :
                viaWidth = cont_size
                viaLength = 4.2
            else :
                viaWidth = vian_size
                viaLength = 4.2
                        
            dbCreateRect(self, Layer(layer, 'drawing'), Box(viaOffset-0.1, corner_end, viaOffset + viaWidth - 0.1, w - corner_end))
            dbCreateRect(self, Layer(layer, 'drawing'), Box(corner_end, viaOffset-0.1, l - corner_end, viaOffset + viaWidth - 0.1))
            dbCreateRect(self, Layer(layer, 'drawing'), Box(l - viaOffset+0.1, corner_end, l - viaWidth - viaOffset + 0.1, w - corner_end))
            dbCreateRect(self, Layer(layer, 'drawing'), Box(corner_end, w - viaOffset+0.1, l - corner_end, w - viaWidth - viaOffset + 0.1))


        if wfill > 0. :    # draw fillers
            distance_edgeseal = self.techparams['MFil_c']
            id = dbCreatePolygon(self, 'Metal1', PointList([Point(metalOffset, metalOffset), Point(metalOffset, metalOffset+16.8), Point(metalOffset+16.8, metalOffset)]))
            # ActFiller and GatFiller
            distance_edgeseal = self.techparams['GFil_d']   
            fillerList = DrawFillers(self, Layer('Activ', 'filler'),   metalOffset-wfill, -wfill+0.8+metalOffset,  l-metalOffset, metalOffset-distance_edgeseal-0.8,  3.4, 3.4,  1.6, 1.6, 'h', 1, True)
            item_list  = DrawFillers(self, Layer('GatPoly', 'filler'), metalOffset-wfill+1, -wfill+metalOffset,  l-metalOffset-1, metalOffset-distance_edgeseal,  1.4, 5,  3.6, 0,  'h', 1, True)
            fillerList += item_list
            item_list = DrawFillers(self, Layer('Activ', 'filler'), metalOffset-wfill+1, metalOffset-0.9,  metalOffset-1.8, w+wfill-metalOffset,  3.4, 3.4,  1.6, 1.6,   'v', 1, True)
            fillerList += item_list
            item_list = DrawFillers(self, Layer('GatPoly', 'filler'), metalOffset-wfill+0.2, metalOffset+0.1,  metalOffset-1.0, w+wfill-metalOffset-1.0, 5, 1.4, 0, 3.6, 'v', 1, True)
            fillerList += item_list
            
            # M1Filler - M5Filler
            layers = ['Metal1', 'Metal2', 'Metal3', 'Metal4', 'Metal5']
            filler_height = self.techparams['MFil_a1']
            filler_width = self.techparams['MFil_a2']
            filler_space = 1.2
            distance_edgeseal = self.techparams['MFil_c']
            distance_edgeseal = self.techparams['MFil_b']
            for layer in layers :
                item_list = DrawFillers(self, Layer(layer, 'filler'), metalOffset-wfill, -wfill+metalOffset, l-metalOffset, metalOffset-distance_edgeseal , filler_width, filler_height, filler_space, filler_space, 'h', 1, True)
                fillerList += item_list
                item_list = DrawFillers(self, Layer(layer, 'filler'), metalOffset-wfill, metalOffset+0.8, metalOffset-filler_space, w+wfill-metalOffset, filler_height, filler_width, filler_space, filler_space, 'v', 1, True)
                fillerList += item_list
                idlist = DrawFillers(self, Layer(layer, 'filler'), metalOffset, metalOffset, metalOffset+16.8, metalOffset+16.8, filler_height, filler_height, filler_space, filler_space, 'h', 0, True)
                item_list = dbLayerInside(self, Layer(layer, 'filler'), idlist, id)
                fillerList += item_list
                for i in idlist :
                    dbDeleteObject(i)
                    
            # TopMet1Filler   
            filler_height = self.techparams['TM1Fil_a']
            filler_width = self.techparams['TM1Fil_a1']
            filler_space = 3.
            distance_edgeseal = self.techparams['TM1Fil_c']
            
            item_list = DrawFillers(self, Layer('TopMetal1', 'filler'), metalOffset-wfill, -wfill+metalOffset,  l-metalOffset, metalOffset-distance_edgeseal,  filler_width, filler_height, filler_space, filler_space, 'h', 1, True)
            fillerList += item_list
            item_list = DrawFillers(self, Layer('TopMetal1', 'filler'), metalOffset-wfill, metalOffset+0.8, metalOffset-filler_space, w+wfill-metalOffset, filler_height, filler_width, filler_space, filler_space, 'v', 1, True)
            fillerList += item_list
            item_list = dbCreateRect(self, Layer('TopMetal1', 'filler'), Box(metalOffset, metalOffset, metalOffset+5, metalOffset+5))
            fillerList.append(item_list)
            # TopMet2Filler
            item_list = DrawFillers(self, Layer('TopMetal2', 'filler'), metalOffset-wfill, -wfill+metalOffset,  l-metalOffset, metalOffset-distance_edgeseal,  filler_width, filler_height, filler_space, filler_space,  'h', 1, True)
            fillerList += item_list
            item_list = DrawFillers(self, Layer('TopMetal2', 'filler'), metalOffset-wfill, metalOffset+0.8, metalOffset-filler_space, w+wfill-metalOffset, filler_height, filler_width, filler_space, filler_space, 'v', 1, True)
            fillerList += item_list
            item_list = dbCreateRect(self, Layer('TopMetal2', 'filler'), Box(metalOffset, metalOffset, metalOffset+5, metalOffset+5))
            fillerList.append(item_list)

            dbDeleteObject(id)
            
            ihpCopyFig(fillerList, Point(l, w), 'R180')
