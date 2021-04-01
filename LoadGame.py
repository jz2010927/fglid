 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os

class LoadGame(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.id = 2
    
    def updateVars(self):
        super().updateVars()
        self.saveList = self.data.loadSaveList()
    
    def bottomButtons(self):
        buttonWidth, buttonHeight = 100, 62
        back = self.drawButton(
            surface=self.surface, x=50, y=self.height-buttonHeight-50, width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['back'], shading=True
        )
        delete = self.drawButton(
            surface=self.surface, x=self.width/2-buttonWidth/2, y=self.height-buttonHeight-50, width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['delete'], shading=True
        )
        load = self.drawButton(
            surface=self.surface, x=self.width-buttonWidth-50, y=self.height-buttonHeight-50, width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['load'], shading=True
        )
        if back:
            return 0
        if load:
            self.data.load(self.chosenSave)
            return 6
        if delete:
            savePath = os.path.join('save', self.chosenSave+'.cundang')
            if os.path.exists(savePath):
                os.remove(savePath)
                self.saveList = self.data.loadSaveList()
                if self.saveList:
                    self.chosenSave = self.saveList[0]
        return self.id

    def drawSaveList(self):
        self.surface.fill(self.colors['棕'])
        self.displaySaveList(x=0, y=20, width=self.width, height=self.height-150)

    def update(self):
        super().update()
        gotoID = self.id
        self.drawSaveList()
        gotoID = self.bottomButtons()
        if gotoID != self.id:
            self.changeScene = True
        return gotoID