 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os

class Tutorial(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.id = 4
    
    def updateVars(self):
        super().updateVars()

    def display(self):
        self.surface.fill(self.colors['黑'])
        Ts = []
        txtFileName = 'Tutorial_' + self.data.settings['language'] + '.txt'
        with open(os.path.join('assets', txtFileName), 'r', encoding='utf-8') as f:
            Ts = f.readlines()
        Ts.append('==>'+self.data.language['right click back']+'<== ')
        fontSize = 20 if self.data.settings['language'] == 'zhCN' else 17
        for i,t in enumerate(Ts):
            self.drawText(
                font=self.fonts[fontSize], text=t[:-1], 
                color=self.colors['白'], x=100, y=70+90*i, 
                surface=self.surface, alpha=255
            )

    def update(self):
        super().update()
        gotoID = self.id
        self.display()
        if pg.mouse.get_pressed()[2] == 1:
            gotoID = 0
        return gotoID

