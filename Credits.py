 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, random

class Credits(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.id = 5
    
    def updateVars(self):
        super().updateVars()

    def readCredits(self):
        path = os.path.join('assets', 'Credits.txt')
        with open(path, 'r', encoding='utf-8') as f:
            self.credits = f.readlines()
    
    def displayCredits(self):
        self.surface.fill(self.colors['黑'])
        textWidth, textHeight = self.fonts[20].size(self.data.language['right click back'])
        self.drawText(
            font=self.fonts[20], text=self.data.language['right click back'], color=self.colors['白'], 
            x=self.width/2-textWidth/2, y=self.height/10+textHeight/2, alpha=255-random.randint(0, 100), surface=self.surface
        )
        for i, text in enumerate(self.credits):
            textWidth, textHeight = self.fonts[27].size(text.strip())
            self.drawText(
                font=self.fonts[27], text=text.strip(), color=self.colors['白'], 
                x=self.width/2-textWidth/2+random.randint(-2, 2), y=self.height/2-150+50*i+random.randint(-2, 2), alpha=random.randint(200, 255), surface=self.surface
            )

    def update(self):
        super().update()
        gotoID = self.id
        self.readCredits()
        self.displayCredits()
        if pg.mouse.get_pressed()[2] == 1: # 单击
            gotoID = 0
            self.changeScene = True
        return gotoID
