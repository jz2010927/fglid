 # -*- coding: utf-8 -*-
from GameObject import GameObject
import pygame as pg, os, math

class Bullet(GameObject):
    def __init__(self, data, surface, camera, startPos, targetPos):
        super().__init__(data, surface, camera)
        self.image = pg.transform.scale(self.data.images['bullet 0'].convert_alpha(), (25, 25))
        self.rect = pg.Rect(self.x, self.y, 25, 25)
        self.destroyed = False
        self.startPos = startPos
        self.targetPos = targetPos
        self.x, self.y = self.startPos
        # self.timePassed = 1000
        self.speed = 10
        self.speedX, self.speedY = self.calculateDirectionVector()
    
    def check(self):
        # self.timePassed -= 1
        travelDistance = self.calculateDistance(*self.startPos, self.x, self.y)
        if travelDistance > self.data.playerTotalValues['attack range']:
            self.destroyed = True

    def calculateDistance(self, x0, y0, x1, y1):
        return math.sqrt((x1-x0)**2+(y1-y0)**2)

    def calculateDirectionVector(self):
        totalDistance = self.calculateDistance(*self.startPos, *self.targetPos)
        x_ratio, y_ratio = (self.targetPos[0]-self.startPos[0])/totalDistance, (self.targetPos[1]-self.startPos[1])/totalDistance
        return self.speed * x_ratio, self.speed * y_ratio

    def move(self):
        self.x += self.speedX
        self.y += self.speedY

    def update(self):
        x, y = self.camera.stickToCamera(x=self.x, y=self.y)
        self.surface.blit(self.image, (x, y))
        self.rect.x, self.rect.y = self.x, self.y
        self.move()
        self.check()
        super().update()