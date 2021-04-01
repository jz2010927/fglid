 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, copy

class NewGame(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.id = 1
        self.userInput, self.insertPosMark = '', '|'
        self.inputMaxLength = 20
        self.profileImageSize = (64, 64)
        self.profileImages = [
            pg.transform.scale(self.data.images['touxiang'+str(i)].convert_alpha(), self.profileImageSize) for i in range(1, 22)
        ]
        self.profileImageIndex = 0
        self.leftArrowImg = (
            self.data.images['left arrow'].convert_alpha(), 
            self.data.images['left arrow clicked'].convert_alpha()
        )
    
    def updateVars(self):
        super().updateVars()
        self.data.playerSave = self.data.defaultPlayerSave
        
    def chooseProfileImg(self):
        width = 250
        arrowSize = (32, 32)
        leftArrow, leftArrowClicked = pg.transform.scale(self.leftArrowImg[0], arrowSize), pg.transform.scale(self.leftArrowImg[1], arrowSize)
        self.drawText(
            surface=self.surface, font=self.fonts[20], text=self.data.language['choose profile image'], 
            color=self.colors['黑'], x=self.width/2, y=self.height/2-self.profileImageSize[0]-20, alpha=255
        )
        self.profileImageIndex = self.arrowSelect(
            surface=self.surface, x=self.width/2-width/2, y=self.height/2, width=width, 
            leftArrowImg=leftArrow, clickedLeftArrowImg=leftArrowClicked, 
            currentIndex=self.profileImageIndex, listLength=len(self.profileImages)
        )
        self.surface.blit(self.profileImages[self.profileImageIndex], (self.width/2-self.profileImageSize[0]/2+arrowSize[0]/2, self.height/2-self.profileImageSize[1]/2))

    def textInput(self):
        self.drawText(
            surface=self.surface, font=self.fonts[20], text=self.data.language['input name']+': ', 
            color=self.colors['黑'], x=self.width/4, y=self.height-250, alpha=255
        )
        if len(self.userInput) >= self.inputMaxLength:
            self.userInput = self.userInput[:self.inputMaxLength]
            self.drawText(
                surface=self.surface, font=self.fonts[20], text=self.data.language['max name length'], 
                color=self.colors['黑'], x=self.width/2-70, y=self.height/2, alpha=255
            )
        else:
            if self.eventInput['KEY_UNICODE'] != None:
                self.userInput += self.eventInput['KEY_UNICODE']
            if pg.key.get_pressed()[pg.K_BACKSPACE]:
                if len(self.userInput) > 0:
                    self.userInput = self.userInput[:-1]
            if pg.key.get_pressed()[pg.K_DELETE]:
                if len(self.userInput) > 0:
                    self.userInput = self.userInput[1:]
        self.drawText(
            surface=self.surface, font=self.fonts[20], text=self.userInput+self.insertPosMark, 
            color=self.colors['黑'], x=self.width/4+150, y=self.height-250, alpha=255
        )

    def drawBottomButtons(self):
        buttonWidth, buttonHeight = 150, 90
        buttonNames = (self.data.language['back'], self.data.language['clear'], self.data.language['start'])
        buttonGoto = (0, self.id, 6)
        gotoID = self.id
        for i in range(len(buttonNames)):
            name, goto = buttonNames[i], buttonGoto[i]
            isClicked = self.drawButton(
                surface=self.surface, x=self.width*(i+1)/(len(buttonNames)+1)-buttonWidth/2, y=self.height-buttonHeight-10, 
                width=buttonWidth, height=buttonHeight, depth=3, 
                text=name, shading=True
            )
            if isClicked:
                gotoID = goto
                if gotoID == 6:
                    self.data.playerSave = copy.deepcopy(self.data.defaultPlayerSave)
        return gotoID

    def update(self):
        super().update()
        self.surface.fill(self.colors['白绿2'])
        gotoID = self.id
        self.chooseProfileImg()
        self.textInput()
        gotoID = self.drawBottomButtons()
        if gotoID == 6:
            self.data.playerSave['profile image'] = self.profileImageIndex + 1
            if len(self.userInput):
                self.data.playerSave['name'] = self.userInput
            else:
                self.data.playerSave['name'] = self.data.language['zhang3']
        return gotoID