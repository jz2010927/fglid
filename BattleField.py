 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, random, copy
from UserPlayer import UserPlayer
from AiPlayer import AiPlayer
from Item import Item
from InGameUI import InGameUI
from Map import Map
from InBuildingScreen import InBuildingScreen
from Bullet import Bullet

class BattleField(GameBase):
    def __init__(self, data, surface, camera):
        super().__init__(data, surface)
        self.id = 6
        self.camera = camera
        self.isHunting = False
        self.player = UserPlayer(data=self.data, surface=self.surface, camera=self.camera, animation=self.loadAnim('player'), imageSize=(90, 150))
        self.ui = InGameUI(data=self.data, surface=self.surface, camera=self.camera, player=self.player)
        self.map = Map(data=self.data, surface=self.surface, camera=self.camera)
        # self.monster = AiPlayer(data=self.data, surface=self.surface)
        # self.item = Item(data=self.data, surface=self.surface)
        self.mainbaseMenu = InBuildingScreen(data=self.data, surface=self.surface, camera=self.camera)
        self.mapIndex = self.map.battleType
        self.classes = (self.map, self.player, self.ui, self.mainbaseMenu)
        self.items = []
        self.monsters = []
        self.bullets = []
        pg.time.set_timer(pg.USEREVENT, 300) # player update anim
        pg.time.set_timer(pg.USEREVENT+1, 1000-self.data.defaultMonster['attack speed']) # monster attack speed
        pg.time.set_timer(pg.USEREVENT+2, 1000) # player hp recovery
        pg.time.set_timer(pg.USEREVENT+3, 1000-self.data.playerTotalValues['attack speed']) # player attack speed
        self.playerBeingHit, self.playerGetDamages = False, []
        self.bgmLoaded = False
    
    def updateVars(self):
        super().updateVars()
        self.bgmLoaded = False
        self.items, self.monsters, self.bullets = [], [], []
        for c in self.classes:
            c.updateVars()
        # for item in self.data.playerSave['backpack']:
        #     item.updateVars()
    
    def passEventInput(self):
        for c in self.classes:
            c.eventInput = self.eventInput

    def loadAnim(self, name):
        idleLeft = [img.convert_alpha() for k, img in self.data.images.items() if name+' idle' in k]
        walkLeft = [img.convert_alpha() for k, img in self.data.images.items() if name+' walk' in k]
        attackLeft = [img.convert_alpha() for k, img in self.data.images.items() if name+' attack' in k]
        getHitLeft = [img.convert_alpha() for k, img in self.data.images.items() if name+' get hit' in k]
        animation = {
            'idle': {'left': idleLeft, 'right': [pg.transform.flip(img, True, False) for img in idleLeft]}, 
            'walk': {'left': walkLeft, 'right': [pg.transform.flip(img, True, False) for img in walkLeft]},
            'attack': {'left': attackLeft, 'right': [pg.transform.flip(img, True, False) for img in attackLeft]},
            'get hit': {'left': getHitLeft, 'right': [pg.transform.flip(img, True, False) for img in getHitLeft]}
        }
        return animation

    def genMonster(self):
        if self.mapIndex != self.map.battleType:
            self.monsters, self.items = [], []
            monsterNum, monsterType = self.map.randomMonsters()
            monsterAttr = copy.deepcopy(self.data.defaultMonster)
            if monsterNum != None:
                imageSize = (90, 150)
                monsterAttr['type'] = 1
                if 'boss' in monsterType:
                    imageSize = (125, 200)
                    monsterAttr['type'] = 0
                for _ in range(monsterNum):
                    monsterAttr['level'] = random.randint(int(self.data.playerSave['main base level']*0.9), self.data.playerSave['main base level'])
                    monsterAttr['quality'] = random.choices([i for i in range(11)], weights=[i*2.72 for i in range(10, -1, -1)], k=1)[0]
                    monster = AiPlayer(
                        data=self.data, surface=self.surface, camera=self.camera, 
                        animation=self.loadAnim(monsterType), imageSize=imageSize, attr=monsterAttr
                    )
                    monster.x, monster.y = self.map.randomXY(range=(100, 1000))
                    # print('monster x, y: ', monster.x, ' ', monster.y)
                    self.monsters.append(monster)
            self.mapIndex = self.map.battleType

    def updatePlayerAnim(self):
        self.player.updateAnim()
        
    def updateMonsterAnim(self):
        if self.monsters:
            for i in range(len(self.monsters)):
                self.monsters[i].updateAnim()
                # 检测是否击中玩家
                monsterElements = {k:v for k, v in self.monsters[i].attr.items() if 'element_' in k}
                if self.playerBeingHit:
                    for damage in self.playerGetDamages:
                        self.player.getHit(damage=damage, elements=monsterElements)
                    self.playerBeingHit = False
                    self.playerGetDamages = []

    def checkBulletCollision(self):
        for m in self.monsters:
            for b in self.bullets:
                if b.rect.colliderect(m.rect):
                    b.destroyed = True
                    # 检测是否击中怪物
                    playerElements = {k:v for k, v in self.data.playerTotalValues.items() if 'element_' in k}
                    critical = self.isHappening(chance=self.data.playerTotalValues['critical chance'])
                    attackDamage = self.data.playerTotalValues['attack']
                    if critical:
                        attackDamage *= self.data.playerTotalValues['critical multiplier']
                    m.getHit(damage=int(round(attackDamage, 0)), elements=playerElements, critical=critical)

    def playerShoot(self):
        # # 按下左键, 生成子弹
        if pg.mouse.get_pressed()[0] == 1:
            offsetX = 90 if self.player.facing == 'right' else 0
            startX, startY = self.player.x+offsetX,self.player.y+75
            targetX, targetY = self.camera.x + pg.mouse.get_pos()[0], self.camera.y + pg.mouse.get_pos()[1]
            self.bullets.append(Bullet(data=self.data, surface=self.surface, camera=self.camera, startPos=(startX, startY), targetPos=(targetX, targetY)))
            self.data.sounds['shoot'].play()

    def playerHpRecovery(self):
        self.data.playerSave['current hp'] = self.player.recovery(
            value=self.data.playerSave['current hp'], maxValue=self.data.playerTotalValues['max hp'], recoveryValue=self.data.playerTotalValues['hp recovery']
        )
        # 顺便
        self.ui.insertPosMark = '' if self.ui.insertPosMark == '|' else '|'

    def addItems(self, attrs, x, y, limitX, limitY):
        for attr in attrs:
            item = Item(data=self.data, surface=self.surface, camera=self.camera, attr=attr)
            item.x, item.y = x+random.randint(-100, 100), y+random.randint(-100, 100)
            if item.x < 0:
                item.x = 0
            if item.x >= limitX:
                item.x = limitX - 50
            if item.y < 0:
                item.y = 0
            if item.y >= limitY:
                item.y = limitY - 50
            self.items.append(item)

    def pickUpItem(self, item):
        conditions = (
            item.rect.collidepoint(pg.mouse.get_pos()), 
            pg.mouse.get_pressed()[0] == 1, 
            self.data.holdingItem == None
        )
        if all(conditions):
            self.data.sounds['pickup item'].play()
            item.location = 'in backpack'
            item.updateVars()
            if item.attr['amount'] > 0 and self.data.playerSave[item.attr['key word']] < self.data.gameAttrRange['user money range'][1]:
                self.data.playerSave[item.attr['key word']] += item.attr['amount']
                self.items.remove(item)
                if self.data.playerSave[item.attr['key word']] > self.data.gameAttrRange['user money range'][1]:
                    self.data.playerSave[item.attr['key word']] = self.data.gameAttrRange['user money range'][1]
            else:
                for page in range(len(self.data.playerSave['backpack'])):
                    for space in range(len(self.data.playerSave['backpack'][page])):
                        if self.data.playerSave['backpack'][page][space] == None:
                            self.data.playerSave['backpack'][page][space] = item.attr
                            self.items.remove(item)
                            return

    # def releaseHoldingItem(self):
    #     conditions = (
    #         self.data.holdingItem != None, 
    #         pg.mouse.get_pressed()[2] == 1
    #     )
    #     if all(conditions):
    #         place = self.data.holdFromPlace['place']
    #         if self.data.holdFromPlace['page'] != None:
    #             page = self.data.holdFromPlace['page']
    #             index = self.data.holdFromPlace['index']
    #             self.data.playerSave[place][page][index] = self.data.holdingItem.attr
    #         else:
    #             index = self.data.holdFromPlace['index']
    #             self.data.playerSave[place][index] = self.data.holdingItem.attr
    #         self.data.holdingItem = None
    #         pg.time.wait(200)

    def syncCameraXY(self):
        self.camera.x, self.camera.y = self.player.x-self.width/2+self.player.imageSize[0]/2, self.player.y-self.height/2+self.player.imageSize[1]/2
        self.camera.x = 0 if self.camera.x < 0 else self.camera.x
        self.camera.y = 0 if self.camera.y < 0 else self.camera.y

    def update(self):
        super().update()
        gotoID = self.id
        if not self.bgmLoaded:
            pg.mixer.music.unload()
            pg.mixer.music.load(os.path.join('assets', 'sounds', 'gameBgm.ogg'))
            pg.mixer.music.set_volume(self.data.settings['sound volume'][0] * self.data.settings['sound volume'][1])
            pg.mixer.music.play(-1)
            self.bgmLoaded = True
        self.passEventInput()
        self.genMonster()
        limitX, limitY = self.map.update()
        if self.map.switchedMap:
            self.player.x, self.player.y = self.width/2+1000, 100
            self.camera.x, self.camera.y = 0, 0
            self.items, self.monsters, self.bullets = [], [], []
            self.map.switchedMap = False
        if self.bullets:
            self.checkBulletCollision()
            for b in self.bullets:
                b.update()
                if b.destroyed:
                    self.bullets.remove(b)
        if self.monsters:
            for monster in self.monsters:
                monster.setTarget(self.player.x, self.player.y)
                monster.update()
                if monster.status == 'attack' and monster.rect.colliderect(self.player.rect):
                    self.playerBeingHit = True
                    self.playerGetDamages.append(monster.attr['attack'])
                if monster.isDead:
                    self.data.playerSave['current exp'] += monster.attr['exp'] * self.data.playerTotalValues['exp multiplier']
                    self.addItems(attrs=monster.itemAttributes, x=monster.x, y=monster.y, limitX=limitX, limitY=limitY)
                    self.monsters.remove(monster)
        if self.items:
            for item in self.items:
                item.update()
                self.pickUpItem(item)
        self.player.limitX, self.player.limitY = limitX, limitY
        self.player.update()
        self.syncCameraXY()
        if self.player.isDead:
            self.map.updateVars()
            self.updateVars()
            self.mapIndex = self.map.battleType
            self.player.isDead = False
        # self.camera.moveWithKey(limitX, limitY)
        if self.map.showmainbaseMenu:
            self.map.showmainbaseMenu = self.mainbaseMenu.update()
        gotoID = self.ui.update()
        dontMoveConditions = (
            self.ui.showBackpack, 
            self.ui.showPlayerAttr, 
            self.map.showmainbaseMenu
        )
        if any(dontMoveConditions):
            self.player.canSetTarget = False
            self.map.canSwitchMap = False
        else:
            self.player.canSetTarget = True
            self.map.canSwitchMap = True
        if gotoID == -2:
            gotoID = self.id
            self.map.updateVars()
            self.updateVars()
            self.mapIndex = self.map.battleType
        if gotoID != self.id:
            self.changeScene = True
        return gotoID