 # -*- coding: utf-8 -*-
from Player import Player
import pygame as pg, random

class UserPlayer(Player):
    def __init__(self, data, surface, camera, animation, imageSize):
        super().__init__(data, surface, camera, animation, imageSize)
        self.calculateValues()
        self.image = self.animation['idle']['left'][0]
        self.gunImg = pg.transform.scale(self.data.images['player water gun'].convert_alpha(), (100, 50))
        self.targetImage = pg.transform.scale(self.data.images['target'].convert_alpha(), (32, 32))
        self.resizeAnimImgs(self.animation)
        self.rect = pg.Rect(self.x+self.imageSize[0]//10, self.y+self.imageSize[1]//10, int(self.imageSize[0]*0.9), int(self.imageSize[1]*0.9))
        self.canSetTarget = True
        
    def updateVars(self):
        super().updateVars()
        self.animIndex = 0
        self.calculateValues()
        self.image = self.animation['idle']['left'][0]
        self.targetImage = pg.transform.scale(self.data.images['target'].convert_alpha(), (32, 32))
        self.resizeAnimImgs(self.animation)
        self.rect = pg.Rect(self.x-self.data.playerTotalValues['attack range'], self.y, self.imageSize[0]+2*self.data.playerTotalValues['attack range'], self.imageSize[1])

    def updateAnim(self):
        self.animTotalFrames = len(self.animation[self.status][self.facing])
        super().updateAnim()

    def updateAttr(self):
        self.data.playerSave['levelup exp'] = self.data.playerSave['level'] ** 3
        # self.data.playerSave['exp multiplier'] += 0
        self.data.playerSave['max hp'] += self.data.playerSave['level'] * 100
        self.data.playerSave['attack'] += self.data.playerSave['level']
        self.data.playerSave['defense'] += self.data.playerSave['level']
        # self.data.playerSave['critical chance'] += self.data.playerSave['level']
        # self.data.playerSave['critical multiplier'] += self.data.playerSave['level']
        # self.data.playerSave['dodge chance'] += self.data.playerSave['level']
        # self.data.playerSave['attack speed'] += self.data.playerSave['level']
        # self.data.playerSave['move speed'] += self.data.playerSave['level']
        # self.data.playerSave['attack range'] += self.data.playerSave['level']
        # self.data.playerSave['element_qian'] += self.data.playerSave['level']
        # self.data.playerSave['element_kun'] += self.data.playerSave['level']
        # self.data.playerSave['element_zhen'] += self.data.playerSave['level']
        # self.data.playerSave['element_xun'] += self.data.playerSave['level']
        # self.data.playerSave['element_kan'] += self.data.playerSave['level']
        # self.data.playerSave['element_li'] += self.data.playerSave['level']
        # self.data.playerSave['element_gen'] += self.data.playerSave['level']
        # self.data.playerSave['element_dui'] += self.data.playerSave['level']

    
    def calculateValues(self):
        self.data.playerSave['levelup exp'] = self.data.playerSave['level'] ** 3
        keyWords = {
            'exp multiplier': 10.0, 
            'max hp': self.data.gameAttrRange['user maxHp range'][1], 
            'hp recovery': 999, 
            'attack': 999999999, 
            'defense': 999999999, 
            'critical chance': 0.5, 
            'critical multiplier': 10.0, 
            'dodge chance': 0.5, 
            'attack speed': self.data.gameAttrRange['user attack speed range'][1], 
            'move speed': self.data.gameAttrRange['user move speed range'][1], 
            'attack range': self.data.gameAttrRange['user max range'], 
            'element_qian': self.data.gameAttrRange['element range'][1], 
            'element_kun': self.data.gameAttrRange['element range'][1], 
            'element_zhen': self.data.gameAttrRange['element range'][1], 
            'element_xun': self.data.gameAttrRange['element range'][1], 
            'element_kan': self.data.gameAttrRange['element range'][1], 
            'element_li': self.data.gameAttrRange['element range'][1], 
            'element_gen': self.data.gameAttrRange['element range'][1], 
            'element_dui': self.data.gameAttrRange['element range'][1]
        }
        for key, limit in keyWords.items():
            self.data.playerTotalValues[key] = self.data.playerSave[key]
            for attr in self.data.playerSave['equipment']:
                if attr != None:
                    self.data.playerTotalValues[key] = self.addValueWithLimit(value=self.data.playerTotalValues[key], addNum=attr[key], limit=limit)

    def attack(self):
        super().attack()
        if pg.mouse.get_pressed()[0] == 1:
            if self.status != 'attack':
                self.animIndex = 0
                self.status = 'attack'
            x, y = self.camera.stickToCamera(self.x, self.y)
            if pg.mouse.get_pos()[0] > x:
                self.facing = 'right'
            else:
                self.facing = 'left'

    def setTarget(self):
        super().setTarget()
        if pg.mouse.get_pressed()[2] == 1 and self.canSetTarget:
            x, y = pg.mouse.get_pos()
            self.targetX, self.targetY = x+self.camera.x, y+self.camera.y
        # 防止目标位置
        if (self.targetX, self.targetY) != (None, None):
            targetDisplayX, targetDisplayY = self.camera.stickToCamera(self.targetX-16, self.targetY-32)
            self.surface.blit(self.targetImage, (targetDisplayX, targetDisplayY))

    def control(self):
        self.setTarget()
        self.moveToTarget(self.data.playerTotalValues['move speed'], offsetX=self.imageSize[0]/2, offsetY=self.imageSize[1])
        self.attack()

    def levelUp(self):
        if self.data.playerSave['level'] < self.data.gameAttrRange['user level range'][1]:
            self.timer = 300
            self.data.playerSave['current exp'] -= self.data.playerSave['levelup exp']
            self.data.playerSave['level'] += 1
            self.updateAttr()
            self.data.playerSave['current hp'] = self.data.playerTotalValues['max hp']
            self.calculateValues()
            self.data.sounds['level up'].play()
        else:
            self.data.playerSave['current exp'] = self.data.playerSave['levelup exp']

    def getHit(self, damage, elements):
        super().getHit()
        dodged = self.isHappening(chance=self.data.playerTotalValues['dodge chance'])
        if not dodged:
            realDamage = damage - self.data.playerTotalValues['defense'] if damage > self.data.playerTotalValues['defense'] else 1
            for k, v in elements.items():
                realDamage += v - self.data.playerTotalValues[k] if v > self.data.playerTotalValues[k] else 0
            self.data.playerSave['current hp'] -= realDamage
            # self.data.sounds['get hit'].play()
        return dodged

    def die(self):
        super().die()
        for i in range(5):
            self.data.playerSave['money'+str(i)] = int(self.data.playerSave['money'+str(i)] * 0.75)
        self.revive()

    def revive(self):
        self.data.playerSave['current hp'] = self.data.playerTotalValues['max hp']//2
        self.camera.x, self.camera.y = 0, 0
        self.x, self.y = 100, 100

    def checkValues(self):
        if self.data.playerSave['current exp'] >= self.data.playerSave['levelup exp']:
            self.levelUp()
        if self.data.playerSave['current hp'] <= 0:
            self.die()

    def addHp(self, addNum=0, addPercent=0.0):
        if addPercent != 0.0:
            addNum += self.data.playerTotalValues['max hp'] * addPercent
        self.data.playerSave['current hp'] += int(addNum)
        if self.data.playerSave['current hp'] > self.data.playerTotalValues['max hp']:
            self.data.playerSave['current hp'] = self.data.playerTotalValues['max hp']

    def update(self):
        super().update()
        self.checkValues()
        x, y = self.camera.stickToCamera(self.x, self.y)
        self.control()
        self.image = self.animation[self.status][self.facing][self.animIndex]
        self.rect.x, self.rect.y = self.x-self.data.playerTotalValues['attack range'], self.y
        # if self.camera.checkInScreen(self.x, self.y, *self.image.get_size()):
        self.surface.blit(self.image, (x, y))
        if self.timer > 0:
            self.drawText(
                font=self.fonts[20], text=self.data.language['level up'], 
                color=self.colors['黑'], x=x+20, y=y-15,  
                surface=self.surface, alpha=255
            )
            self.timer -= 1
        if self.status == 'attack':
            gunImg = pg.transform.rotate(self.gunImg, random.randint(-5, 5))
            offsetX = -20
            if self.facing == 'right':
                gunImg = pg.transform.flip(gunImg, True, False)
                offsetX = 20
            self.surface.blit(gunImg, (x+offsetX, y+70))
        if self.data.playerChanged:
            self.calculateValues()
            if self.data.playerSave['current hp'] > self.data.playerTotalValues['max hp']:
                self.data.playerSave['current hp'] = self.data.playerTotalValues['max hp']
            self.data.playerChanged = False