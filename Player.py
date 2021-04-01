 # -*- coding: utf-8 -*-
from GameObject import GameObject
import pygame as pg, random

class Player(GameObject):
    def __init__(self, data, surface, camera, animation, imageSize):
        super().__init__(data, surface, camera)
        self.animIndex = 0
        self.animTotalFrames = 0
        self.defaultStatus = 'idle'
        self.status = 'idle'
        self.facing = 'left'
        self.limitX, self.limitY = 10000, 10000
        self.targetX, self.targetY = None, None
        self.isDead = False
        self.imageSize = imageSize
        self.rect = pg.Rect(self.x, self.y, *self.imageSize)
        self.animation = self.resizeAnimImgs(animation)
    
    def updateVars(self):
        super().updateVars()
        self.isDead = False
        self.targetX, self.targetY = None, None

    def checkStatusAndFacing(self, status, facing=None):
        a = (self.status == status)
        isSame = a
        if facing != None:
            b = (self.facing == facing)
            isSame = a and b
        return isSame

    def resizeAnimImgs(self, animation):
        for k, imgs in animation.items():
            for i in range(len(imgs['left'])):
                try:
                    imgs['left'][i] = pg.transform.scale(imgs['left'][i], self.imageSize)
                    imgs['right'][i] = pg.transform.scale(imgs['right'][i], self.imageSize)
                except:
                    print('error \n', k, ': ', imgs)
        return animation

    def updateAnim(self):
        # print(f'index: {self.animIndex}, total frames: {self.animTotalFrames}')
        if self.animIndex < self.animTotalFrames-1:
            self.animIndex += 1
        else:
            self.animIndex = 0
            self.status = self.defaultStatus

    def move(self, targetX, targetY):
        if self.status != 'walk':
            self.animIndex = 0
            self.status = 'walk'
        if targetX < self.x:
            self.facing = 'left'
        else:
            self.facing = 'right'
        if targetX < 0:
            self.x = 0
        elif targetX > self.limitX:
            self.x = self.limitX
        else:
            self.x = targetX
        if targetY < 0:
            self.y = 0
        elif targetY > self.limitY:
            self.y = self.limitY
        else:
            self.y = targetY
    
    def attack(self):
        pass


    def getHit(self):
        if self.status != 'get hit':
            self.status = 'get hit'
            self.animIndex = 0

    def moveToTarget(self, moveSpeed, offsetX=0, offsetY=0, defaultTargetX=None, defaultTargetY=None):
        if self.targetX == defaultTargetX or self.targetY == defaultTargetY:
            return False
        # 计算玩家落脚点
        sourceX, sourceY = self.x+offsetX, self.y+offsetY
        speed = moveSpeed
        speedX, speedY = 0, 0
        # X
        distanceX = self.targetX-sourceX
        x_direction = 1 if distanceX > 0 else -1
        speedX = abs(distanceX) if abs(distanceX) < speed else speed
        # Y
        distanceY = self.targetY-sourceY
        y_direction = 1 if distanceY > 0 else -1
        speedY = abs(distanceY) if abs(distanceY) < speed else speed
        # move
        self.move(targetX=self.x+speedX*x_direction, targetY=self.y+speedY*y_direction)
        # check
        if int(sourceX) == self.targetX and int(sourceY) == self.targetY:
            self.targetX, self.targetY = defaultTargetX, defaultTargetY
        return True

    def setTarget(self):
        pass

    def recovery(self, value, maxValue, recoveryValue):
        newValue = value
        if value < maxValue:
            if value + recoveryValue <= maxValue:
                newValue += recoveryValue
            else:
                newValue = maxValue
        return newValue
    
    def die(self):
        self.isDead = True

    def update(self):
        super().update()