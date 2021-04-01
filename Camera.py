# -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, math, random

class Camera(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.x, self.y = 0, 0
        self.sqrt = math.sqrt

    def checkInScreen(self, x, y, width, height):
        margin = 10
        objectRect = pg.Rect(x, y, width, height)
        screenRect = pg.Rect(-margin, -margin, self.width+margin, self.height+margin)
        return screenRect.colliderect(objectRect)

    def moveWithKey(self, bgWidth, bgHeight):
        cameraSpeed = self.data.settings['camera speed']
        if pg.key.get_pressed()[self.data.settings['key bindings']['up']]:
            if self.y - cameraSpeed >=0:
                self.y -= cameraSpeed
            else:
                self.y = 0
        if pg.key.get_pressed()[self.data.settings['key bindings']['down']]:
            if self.y + cameraSpeed <= bgHeight - self.height:
                self.y += cameraSpeed
            else:
                self.y = bgHeight - self.height
        if pg.key.get_pressed()[self.data.settings['key bindings']['left']]:
            if self.x - cameraSpeed >= 0:
                self.x -= cameraSpeed
            else:
                self.x = 0
        if pg.key.get_pressed()[self.data.settings['key bindings']['right']]:
            if self.x + cameraSpeed <= bgWidth - self.width:
                self.x += cameraSpeed
            else:
                self.x = bgWidth - self.width

    def calculateDistance(self, fromX, fromY, toX, toY):
        return self.sqrt((toX-fromX)**2+(toY-fromY)**2)
        
    def move(self, x, y):
        self.x, self.y = x, y
    
    def stickToCamera(self, x, y):
        return x-self.x, y-self.y
    
    def shake(self, amplitudeX, amplitudeY, time):
        pass