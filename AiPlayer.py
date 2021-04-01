 # -*- coding: utf-8 -*-
from Player import Player
import pygame as pg, random, copy

class AiPlayer(Player):
    def __init__(self, data, surface, camera, animation, imageSize, attr):
        super().__init__(data, surface, camera, animation, imageSize)
        self.attackDistance, self.huntDistance = 100, 200
        self.playerX, self.playerY = self.targetX, self.targetX
        self.attr = copy.deepcopy(attr)
        self.calculateAttr()
        self.totalHp = self.attr['hp']
        self.damageText = ''
        self.damageCritical = False
        self.damageTextX, self.damageTextY = 0, 0
        self.itemAttributes = []
        self.element_icon = pg.transform.scale(self.data.images[self.attr['element']], (64, 64)).convert_alpha()

    def updateVars(self):
        super().updateVars()
    
    def calculateAttr(self):
        amp = 1
        # is boss
        if self.attr['type'] == 0:
            amp = 3
        self.attr['exp'] = (self.attr['level']+1) * (self.attr['quality']+1) * amp
        self.attr['attack'] = (self.attr['level'] + 1) * amp + self.attr['quality']
        self.attr['defense'] = (self.attr['level'] + self.attr['quality']) * amp
        self.attr['attack speed'] = (self.attr['level']//10 + self.attr['quality'] + 50) * amp
        self.attr['dodge chance'] = 0.1 * amp
        self.attr['move speed'] = (10 + self.attr['quality']) * amp
        self.attr['hp'] = ((self.attr['level']+1) * (self.attr['quality']+1)) ** (amp + 1)
        elements = (
            'element_qian', 'element_kun', 'element_zhen', 'element_xun', 
            'element_kan', 'element_li', 'element_gen', 'element_dui'
        )
        element = random.choice(elements)
        self.attr['element'] = element
        self.attr[element] = (random.randint(0, self.attr['level'] + self.attr['quality'] + 1) * amp) // 10
        # limit
        self.attr['attack'] = self.attr['attack'] if self.attr['attack'] <= self.data.gameAttrRange['user maxHp range'][1]//2 else self.data.gameAttrRange['user maxHp range'][1]//2
        self.attr['defense'] = self.attr['defense'] if self.attr['defense'] <= self.data.gameAttrRange['user maxHp range'][1]//2 else self.data.gameAttrRange['user maxHp range'][1]//2
        self.attr['attack speed'] = self.attr['attack speed'] if self.attr['attack speed'] <= self.data.gameAttrRange['user attack speed range'][1]//2 else self.data.gameAttrRange['user attack speed range'][1]//2
        self.attr['dodge chance'] = self.attr['dodge chance'] if self.attr['dodge chance'] <= 0.5 else 0.5
        self.attr['move speed'] = self.attr['move speed'] if self.attr['move speed'] <= self.data.gameAttrRange['user move speed range'][1]//2 else self.data.gameAttrRange['user move speed range'][1]//2
        self.attr[element] = self.attr[element] if self.attr[element] <= self.data.gameAttrRange['element range'][1] else self.data.gameAttrRange['element range'][1]

    def displayHp(self):
        width, height = self.imageSize[0]*(self.attr['hp']/self.totalHp), 20
        x, y = self.camera.stickToCamera(self.x, self.y-height)
        pg.draw.rect(surface=self.surface, color=self.colors['红'], rect=(x, y, width, height))
    
    def displayLevelAndQuality(self):
        levelTextWidth, levelTextHeight = self.fonts[15].size('Lvl. '+str(self.attr['level']))
        textX, textY = self.camera.stickToCamera(x=self.x+self.imageSize[0]/2-levelTextWidth/2, y=self.y-levelTextHeight-50)
        self.drawText(
            surface=self.surface, font=self.fonts[15], text='Lvl. '+str(self.attr['level']), 
            color=self.colors['黑'], x=textX, y=textY, alpha=255
        )
        qualityBg = self.data.images['quality bg'+str(self.attr['quality'])].convert_alpha()
        qualityBg = pg.transform.scale(qualityBg, (int(self.imageSize[0]*1.5), int(self.imageSize[1]*0.3)))
        bgX, bgY = self.camera.stickToCamera(int(self.x-self.imageSize[0]/4), int(self.y+self.imageSize[1]-qualityBg.get_height()/2-10))
        self.surface.blit(qualityBg, (bgX, bgY))

    def huntPlayer(self):
        distance = self.camera.calculateDistance(self.x, self.y, self.playerX, self.playerY)
        if distance < self.huntDistance:
            self.targetX, self.targetY = self.playerX, self.playerY
            offset = self.imageSize[0]*0.6 if self.targetX > self.x else -self.imageSize[0]*0.6
            self.moveToTarget(self.data.defaultMonster['move speed'], offsetX=offset)
            if distance < self.attackDistance:
                self.attack()

    def attack(self):
        super().attack()
        if self.status != 'attack':
            self.animIndex = 0
            self.status = 'attack'
        try:
            if self.playerX > self.x:
                self.facing = 'right'
            else:
                self.facing = 'left'
        except:
            print(self.targetX, ' ', self.targetY)
            self.targetX, self.targetY = self.x, self.y

    def setTarget(self, x, y):
        super().setTarget()
        self.playerX, self.playerY = x, y

    def displayDamage(self):
        damageFontSize = 15
        damageText = self.damageText
        if self.damageCritical:
            damageFontSize = 20
            damageText = self.data.language['critical hit'] + ' ' +  self.damageText
        self.drawText(
            surface=self.surface, font=self.fonts[damageFontSize], text=damageText, 
            color=self.colors['黑'], x=self.damageTextX, y=self.damageTextY, alpha=255
        )

    def getHit(self, damage, elements, critical=False):
        super().getHit()
        self.damageTextX, self.damageTextY = self.camera.stickToCamera(self.x+self.imageSize[0]/2+random.randint(-50, 50), self.y+self.imageSize[1]/2+random.randint(-50, 50))
        dodged = self.isHappening(chance=self.attr['dodge chance'])
        if not dodged:
            self.damageCritical = critical
            self.timer = 100
            realDamage = damage - self.attr['defense'] if damage > self.attr['defense'] else 1
            for k, v in elements.items():
                realDamage += v - self.attr[k] if v > self.attr[k] else 0
            self.damage = realDamage
            self.attr['hp'] -= realDamage
            self.damageText = str(realDamage)
            self.data.sounds['get hit'].play()
        else:
            self.damageText = self.data.language['miss']
            self.damageCritical = False
        return dodged
    
    def die(self):
        super().die()
        self.attr['hp'] = 0
        self.itemAttributes = self.createItems()

    def randomEquipment(self):
        itemAttr = copy.deepcopy(self.data.defaultItemAttr)
        itemAttr['type'] = 0
        itemAttr['key word'] = random.choice(tuple(self.data.equipmentImgs.keys()))
        itemAttr['random name index'] = 'common name'+str(random.randint(0, 20))
        itemAttr['quality'] =random.randint(0, self.attr['quality'])
        elements = (
            'qian', 'kun', 'zhen', 'xun', 
            'kan', 'li', 'gen', 'dui'
        )
        element = 'element_' + random.choice(elements)
        minElement, maxElement = itemAttr['quality']+1, (itemAttr['quality']+1) * 90
        itemAttr['element'] = element
        itemAttr[element] = random.randint(minElement, maxElement)
        attrOptions = (
            'attack speed', 'critical chance', 'critical multiplier',
            'dodge chance', 'move speed', 'max hp', 'exp multiplier', 'attack range', 'hp recovery'
        )
        minAttrNum = (itemAttr['quality']//2)+1 if (itemAttr['quality']//2)+1 <= len(attrOptions) else len(attrOptions)
        maxAttrNum = itemAttr['quality']+1 if itemAttr['quality']+1 <= len(attrOptions) else len(attrOptions)
        attrNum = random.randint(minAttrNum, maxAttrNum)
        attrsChosen = random.sample(attrOptions, attrNum)
        for key in attrsChosen:
            if type(itemAttr[key]) == float:
                itemAttr[key] = random.uniform(0.01, (itemAttr['quality']+1)/(self.data.gameAttrRange['item quality range'][1]*10+1))
            else:
                itemAttr[key] = random.randint(1, (itemAttr['quality']+2))
                if key == 'attack speed':
                    itemAttr[key] *= 10
        return itemAttr

    def randomConsumable(self, keyName=None):
        itemAttr = copy.deepcopy(self.data.defaultItemAttr)
        itemAttr['type'] = 1
        randomWeight = random.random()
        consumableKeyName = random.choice(tuple(self.data.consumableImgs.keys())) if keyName == None else keyName
        itemAttr['key word'] = consumableKeyName
        itemAttr['quality'] = random.randint(0, self.attr['quality'])
        attrOptions = ('hp', 'exp')
        minAttrNum = (itemAttr['quality']//2)+1 if (itemAttr['quality']//2)+1 <= len(attrOptions) else len(attrOptions)
        maxAttrNum = itemAttr['quality']+1 if itemAttr['quality']+1 <= len(attrOptions) else len(attrOptions)
        attrNum = random.randint(minAttrNum, maxAttrNum)
        attrsChosen = random.sample(attrOptions, attrNum)
        for key in attrsChosen:
            itemAttr[key] = random.randint((itemAttr['quality']+1), (itemAttr['quality']+1)*100)
        if itemAttr['quality'] > 5:
            maxHpPercentValue = (itemAttr['quality']+1)/(self.data.gameAttrRange['item quality range'][1]+1)
            itemAttr['hp percent'] = random.uniform(maxHpPercentValue//10, maxHpPercentValue)
        if itemAttr['quality'] > 7:
            maxExpPercentValue = (itemAttr['quality']+1)/(self.data.gameAttrRange['item quality range'][1]+1)
            itemAttr['exp percent'] = random.uniform(maxExpPercentValue//10, maxExpPercentValue)
        if consumableKeyName == 'consumable doge' or consumableKeyName == 'consumable answer sheet':
            itemAttr['amount'] = 0
            itemAttr['quality'] = 9
            itemAttr['hp'] = 0
            itemAttr['hp percent'] = 0
            itemAttr['exp'] = 0
        return itemAttr

    def randomResources(self):
        itemAttr = copy.deepcopy(self.data.defaultItemAttr)
        itemAttr['type'] = 2
        itemAttr['quality'] = 1
        itemAttr['amount'] = random.randint((self.attr['level']//2)+1, (self.attr['level']+100))
        moneyKeyName = random.choice(tuple(self.data.moneyImgs.keys()))
        itemAttr['key word'] = moneyKeyName
        return itemAttr

    def randomCard(self):
        itemAttr = copy.deepcopy(self.data.defaultItemAttr)
        itemAttr['type'] = 3
        itemAttr['quality'] = 5
        cardKeyName = random.choice(tuple(self.data.pokerCardImgs.keys()))
        itemAttr['key word'] = cardKeyName
        return itemAttr

    def createItems(self):
        items = []
        itemNumMin, itemNumMax = -1, self.attr['quality']+1
        if self.attr['type'] == 0:
            itemNumMin += 3
            itemNumMax += 3
        itemNum = random.randint(itemNumMin, itemNumMax)
        if itemNum > 0:
            for _ in range(itemNum):
                itemAttr = None
                itemType = random.random()
                # itemType = random.randint(0, 3) # 0 equipment, 1 consumable, 2 money, 3 card
                if itemType <= 0.2:
                    itemAttr = self.randomEquipment()
                elif itemType > 0.2 and itemType <= 0.35:
                    itemAttr = self.randomConsumable()
                elif itemType > 0.35 and itemType <= 0.5:
                    itemAttr = self.randomConsumable(keyName='consumable answer sheet')
                elif itemType > 0.5 and itemType <= 0.9:
                    itemAttr = self.randomResources()
                elif itemType > 0.9:
                    itemAttr = self.randomCard()
                items.append(itemAttr)
        return items

    def checkValues(self):
        if self.attr['hp'] <= 0:
            self.die()
            self.createItems()

    def update(self):
        super().update()
        self.checkValues()
        self.displayHp()
        self.displayLevelAndQuality()
        x, y = self.camera.stickToCamera(self.x, self.y)
        self.image = self.animation[self.status][self.facing][self.animIndex]
        self.rect.x, self.rect.y = self.x, self.y
        # if self.camera.checkInScreen(self.x, self.y, *self.image.get_size()):
        self.surface.blit(self.image, (x, y))
        self.surface.blit(self.element_icon, (x+self.imageSize[0]+10, y-50))
        self.huntPlayer()
        if self.timer > 0:
            self.displayDamage()
            self.timer -= 1
        else:
            self.damageText = ''