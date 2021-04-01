 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, random

class GameObject(GameBase):
    def __init__(self, data, surface, camera):
        super().__init__(data, surface)
        self.camera = camera
        self.x, self.y = 0, 0
    
    def updateVars(self):
        super().updateVars()
    
    def randomName(self):
        return random.choice([name for k, name in self.data.language.items() if 'common name' in k])

    def update(self):
        super().update()