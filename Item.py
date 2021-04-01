 # -*- coding: utf-8 -*-
from GameObject import GameObject
import pygame as pg, random

class Item(GameObject):
    def __init__(self, data, surface, camera, attr):
        super().__init__(data, surface, camera)
        self.attr = attr
        if self.attr['random name index'] != None:
            self.attr['name'] = self.data.language[self.attr['random name index']] + self.data.language['de'] + ' ' + self.data.language[self.attr['key word']]              
        else:
            if 'card_' not in self.attr['key word']:
                self.attr['name'] = self.data.language[self.attr['key word']]
        self.rect = None
        self.location = 'on ground'
        self.imageSize = {
            'on ground': (50, 50), 
            'in backpack': (33, 33), 
            'equipped': (33, 33), 
            'merchant': (64, 64)
        }
        self.bigImgSize = (128, 128)
        imgDictByType = (
            self.data.equipmentImgs, 
            self.data.consumableImgs, 
            self.data.moneyImgs, 
            self.data.pokerCardImgs
        )
        self.img = imgDictByType[self.attr['type']][self.attr['key word']]
        self.imgBig = pg.transform.scale(self.img, self.bigImgSize)
        self.qualityBgBig = pg.transform.scale(self.data.qualityBgImgs['quality bg'+str(self.attr['quality'])], self.bigImgSize)
        self.img = pg.transform.scale(self.img, self.imageSize[self.location])
        self.qualityBg = pg.transform.scale(self.data.qualityBgImgs['quality bg'+str(self.attr['quality'])], self.imageSize[self.location])
        self.element_icon = None
        if self.attr['type'] == 0:
            self.element_icon = pg.transform.scale(self.data.images[self.attr['element']], (64, 64)).convert_alpha()
        self.displayAttributes, self.showName = True, False
        self.resources = [0, 0, 0, 0, 0]
        self.moneyRequired = {
            'level upgrade': (0, 0, 0, 0, 0, 0), 
            'star upgrade': (0, 0, 0, 0, 0, 0)
        }
        
    def updateVars(self):
        super().updateVars()
        self.img = pg.transform.scale(self.img, self.imageSize[self.location])
        self.qualityBg = pg.transform.scale(self.qualityBg, self.imageSize[self.location])
        if self.attr['key word'] == 'consumable doge' or self.attr['key word'] == 'consumable answer sheet':
            self.attr['description'] = self.data.language[self.attr['key word']+' description']
        self.formName()
        self.calculateRecycleResources()
        if self.attr['type'] == 0:
            self.calculateMoneyRequired_Level()
            self.calculateMoneyRequired_Star()
            self.calculateAttr()
    
    def formName(self):
        if self.attr['random name index'] != None:
            self.attr['name'] = self.data.language[self.attr['random name index']] + self.data.language['de'] + ' ' + self.data.language[self.attr['key word']]
        else:
            if 'card_' not in self.attr['key word']:
                self.attr['name'] = self.data.language[self.attr['key word']]
            else:
                if 'Joker' in self.attr['key word']:
                    self.attr['name'] = self.data.language[self.attr['key word']]
                    self.attr['quality'] = 10
                else:
                    poker_suits = {
                        'D': self.data.language['poker diamond'], 
                        'C': self.data.language['poker club'], 
                        'H': self.data.language['poker heart'], 
                        'S': self.data.language['poker spade']
                    }
                    poker_specialNum = {'1':'A', '11':'J', '12':'Q', '13':'K'}
                    poker_number = self.attr['key word'][-3:-1]
                    if poker_number[0] == '0':
                        poker_number = poker_number[1]
                    try:
                        poker_number = poker_specialNum[poker_number]
                        self.attr['quality'] = 7
                    except:
                        pass
                    suit = self.data.language['poker card'] + ' ' + poker_suits[self.attr['key word'][-1]]
                    self.attr['name'] = suit + ' ' + poker_number

    def calculateRecycleResources(self):
        alphabet = {
            'a': '啊', 'b': '吧', 'c': '从', 'd': '的', 'e': '额', 'f': '发', 'g': '给', 'h': '和', 'i': '哎', 'j': '就', 'k': '看', 'l': '了', 'm': '吗', 'n': '你', 
            'o': '哦', 'p': '怕', 'q': '去', 'r': '人', 's': '是', 't': '他', 'u': '与', 'v': '绿', 'w': '我', 'x': '下', 'y': '有', 'z': '在', 
        }
        try:
            for i in range(5):
                r_base = (self.attr['level']+1) * ((self.attr['icon star']+1)**2) * (self.attr['quality']+1)
                letter = self.attr['name'][i] if self.attr['name'][i] not in tuple(alphabet.keys()) else alphabet[self.attr['name'][i]]
                resource = int(r_base * ord(letter)/1000)
                self.resources[i] = resource if resource > 0 else r_base
        except:
            self.resources = [0,0,0,0,0]

    def calculateMoneyRequired_Level(self):
        self.moneyRequired['level upgrade'] = (
            # 木材
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+5) ** 5),
            # 合金 
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+5) ** 5), 
            # 净水
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+5) ** 5), 
            # 食物
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+5) ** 5), 
            # 燃料
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+5) ** 5), 
            # 金条
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+1) ** 1.5)
        )
    
    def calculateMoneyRequired_Star(self):
        self.moneyRequired['star upgrade'] = (
            # 木材
            int((self.attr['level']+self.attr['quality']+1) ** (self.attr['icon star']+1)),
            # 合金 
            int((self.attr['level']+self.attr['quality']+1) ** (self.attr['icon star']+1)), 
            # 净水
            int((self.attr['level']+self.attr['quality']+1) ** (self.attr['icon star']+1)), 
            # 食物
            int((self.attr['level']+self.attr['quality']+1) ** (self.attr['icon star']+1)), 
            # 燃料
            int((self.attr['level']+self.attr['quality']+1) ** (self.attr['icon star']+1)), 
            # 金条
            int((self.attr['level']+self.attr['icon star']+self.attr['quality']+1) ** 3)
        )

    def calculateAttr(self):
        self.attr['attack'] = (self.attr['level']+1) * (self.attr['icon star']+1)
        self.attr['defense'] = (self.attr['level']+1) * (self.attr['icon star']+1)
        self.attr['required level'] = self.attr['icon star']*100 + 1

    def displayAttr(self):
        pos = pg.mouse.get_pos()
        ui_x, ui_y = pos
        ui_width, ui_height = 400, 700
        qualityColor = self.data.qualityColor[self.attr['quality']]
        if pos[0] > self.width/2:
            if pos[1] > self.height/2:
                ui_x, ui_y = pos[0]-ui_width, pos[1]-ui_height
            else:
                ui_x, ui_y = pos[0]-ui_width, pos[1]
        else:
            if pos[1] > self.height/2:
                ui_x, ui_y = pos[0], pos[1]-ui_height
            else:
                ui_x, ui_y = pos
        # 渲染边框
        frame = pg.transform.scale(self.data.images['item attr bg'], (ui_width, ui_height)).convert()
        frame.set_alpha(200)
        self.surface.blit(frame, (ui_x, ui_y))
        # 渲染名称
        itemNameText = self.attr['name']
        if self.attr['type'] == 0:
            itemNameText = self.attr['name']+' +'+str(self.attr['level'])+' ('+self.data.language[self.attr['element']]+')'
        nameWidth, nameHeight = self.fonts[20].size(itemNameText)
        self.drawText(
            surface=self.surface, font=self.fonts[20], text=itemNameText, 
            color=qualityColor, x=ui_x+ui_width/2-nameWidth/2, y=ui_y+nameHeight+20, alpha=255
        )
        # 渲染图片
        # self.qualityBgBig = pg.transform.rotate(self.qualityBgBig, 1)
        self.surface.blit(self.qualityBgBig, (ui_x+ui_width/2-self.bigImgSize[0]/2, ui_y+nameHeight+50))
        self.surface.blit(self.imgBig, (ui_x+ui_width/2-self.bigImgSize[0]/2, ui_y+nameHeight+50))
        # 渲染装备专有
        if self.attr['type'] == 0:
            # 渲染元素图标
            # element_icon = pg.transform.scale(self.data.images[self.attr['element']], (64, 64)).convert_alpha()
            self.surface.blit(self.element_icon, (ui_x+ui_width-40, ui_y-24))
            # 渲染星级
            star = pg.transform.scale(self.data.images['icon star'], (32, 32)).convert_alpha()
            self.surface.blit(star, (ui_x+40, ui_y+nameHeight+self.bigImgSize[1]+50))
            starText = str(self.attr['icon star'])+'/'+str(self.data.gameAttrRange['item star range'][1])
            self.drawText(
                surface=self.surface, font=self.fonts[20], text=starText, 
                color=self.colors['金2'], x=ui_x+75, y=ui_y+int(nameHeight*1.5)+self.bigImgSize[1]+50, alpha=255
            )
            # 渲染品质
            qualityText = self.data.language['quality'] + ' ' + str(self.attr['quality']) + '/' + str(self.data.gameAttrRange['item quality range'][1])
            qualityTextWidth, qualityTextHeight = self.fonts[20].size(qualityText)
            self.drawText(
                surface=self.surface, font=self.fonts[20], text=qualityText, 
                color=qualityColor, x=ui_x+ui_width-qualityTextWidth-50, y=ui_y+int(nameHeight*1.5)+self.bigImgSize[1]+50, alpha=255
            )
            # 渲染属性
            equipmentKeyNeedRender = (
                'attack', 'defense', 'attack speed', 'critical chance', 'critical multiplier',
                'dodge chance', 'move speed', 'max hp', 'exp multiplier', 'required level', 
                'element_qian', 'element_kun', 'element_zhen', 'element_xun', 
                'element_kan', 'element_li', 'element_gen', 'element_dui'
            )
            j = 0
            for k in equipmentKeyNeedRender:
                textColor = self.colors['白']
                if self.attr[k] != 0:
                    mark = '+'
                    if self.attr[k] < 0:
                        mark = '-'
                    if k == 'required level':
                        mark = ''
                        textColor = self.colors['白'] if self.data.playerSave['level'] >= self.attr['required level'] else self.colors['红']
                    numText = str(self.attr[k])
                    if type(self.attr[k]) == float:
                        numText = str(round(self.attr[k]*100, 0)) + '%'
                    attrText = self.data.language[k] + ' ' + mark + ' ' + numText
                    attrTextWidth, attrTextHeight = self.fonts[15].size(attrText)
                    attrTextX = ui_x+ui_width/2-attrTextWidth/2
                    attrTextY = ui_y+self.bigImgSize[1]+120+25*j
                    self.drawText(
                        surface=self.surface, font=self.fonts[15], text=attrText, 
                        color=textColor, x=attrTextX, y=attrTextY, alpha=255
                    )
                    j += 1
        if self.attr['type'] == 1:
            consumableKeyNeedRender = ('exp', 'hp', 'hp percent', 'exp percent')
            j = 0
            for k in consumableKeyNeedRender:
                if self.attr[k] != 0:
                    mark = '+'
                    if self.attr[k] < 0:
                        mark = '-'
                    numText = str(self.attr[k])
                    if type(self.attr[k]) == float:
                        numText = str(round(self.attr[k]*100, 0)) + '%'
                    attrText = self.data.language[k] + ' ' + mark + ' ' + numText
                    attrTextWidth, attrTextHeight = self.fonts[15].size(attrText)
                    attrTextX = ui_x+ui_width/2-attrTextWidth/2
                    attrTextY = ui_y+self.bigImgSize[1]+120+25*j
                    self.drawText(
                        surface=self.surface, font=self.fonts[15], text=attrText, 
                        color=self.colors['白'], x=attrTextX, y=attrTextY, alpha=255
                    )
                    j += 1
        # 渲染描述
        if self.attr['description'] != '':
            textWidth, textHeight = self.fonts[15].size(self.attr['description'])
            self.drawText(
                surface=self.surface, font=self.fonts[15], text=self.attr['description'], 
                color=self.colors['白'], x=ui_x+ui_width/2-textWidth/2, y=ui_y+ui_height-100, alpha=255
            )

    def displayAttrHelper(self):
        if self.location != 'on ground' and self.rect.collidepoint(pg.mouse.get_pos()) and self.displayAttributes:
            self.displayAttr()

    def leftClick(self, i, page=None):
        if self.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0] == 1:
            if self.location != 'on ground' and self.data.holdingItem == None:
                # print(self.resources)
                keyMap = {'in backpack': 'backpack', 'equipped': 'equipment'}
                self.data.holdingItem = self
                self.data.holdFromPlace = {'place':keyMap[self.location], 'page': page, 'index': i}
                if page == None:
                    self.data.playerSave['equipment'][i] = 'occupied'
                else:
                    self.data.playerSave['backpack'][page][i] = 'occupied'
            elif self.data.holdingItem != None:
                if page == None and self.data.playerSave['equipment'][i] == None:
                    self.data.playerSave['equipment'][i] = self.data.holdingItem.attr
                elif page != None and self.data.playerSave['backpack'][page][i] == None:
                    self.data.playerSave['backpack'][page][i] = self.data.holdingItem.attr
                originalPage, originalIndex = self.data.holdFromPlace['page'], self.data.holdFromPlace['index']
                if self.data.holdFromPlace['place'] == 'equipment':
                    self.data.playerSave['equipment'][originalIndex] = None
                elif self.data.holdFromPlace['place'] == 'backpack':
                    self.data.playerSave['equipment'][originalPage][originalIndex] = None
        
    def rightClick(self, i, page=None, player=None):
        if self.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[2] == 1:
            # 刷新装备变更后属性
            self.data.playerChanged = True
            if self.location == 'in backpack':
                if self.attr['type'] == 0 and self.data.playerSave['level'] >= self.attr['required level']:
                    self.data.sounds['change equipment'].play()
                    for j, space in enumerate(self.data.playerSave['equipment']):
                        if space == None:
                            self.data.playerSave['equipment'][j] = self.data.playerSave['backpack'][page][i]
                            self.data.playerSave['backpack'][page][i] = None
                            return
                    else:
                        temp = self.data.playerSave['equipment'][-1]
                        self.data.playerSave['equipment'][-1] = self.data.playerSave['backpack'][page][i]
                        self.data.playerSave['backpack'][page][i] = temp
                        pg.time.wait(200)
                elif self.attr['type'] == 1 and self.attr['key word'] != 'consumable doge' and self.attr['key word'] != 'consumable answer sheet':
                    # 喝药间隔
                    # pg.time.delay(100)
                    soundOptions = ('eat 01', 'eat 02')
                    soundChoice = random.choice(soundOptions)
                    self.data.sounds[soundChoice].play()
                    player.addHp(addNum=self.attr['hp'], addPercent=self.attr['hp percent'])
                    self.attr['exp'] += self.data.playerSave['levelup exp'] * self.attr['exp percent']
                    self.data.playerSave['current exp'] += self.attr['exp']
                    self.data.playerSave['backpack'][page][i] = None
            elif self.location == 'equipped':
                for m, p in enumerate(self.data.playerSave['backpack']):
                    for n, space in enumerate(p):
                        if space == None:
                            self.data.playerSave['backpack'][m][n] = self.data.playerSave['equipment'][i]
                            self.data.playerSave['equipment'][i] = None
                            return
                    
            
    def drawItem(self):
        x, y = self.x, self.y
        if self.location == 'on ground':
            # 物体随镜头移动
            x, y = self.camera.stickToCamera(self.x, self.y)
            # 渲染名字
            amount = '' if self.attr['amount'] == 0 else str(self.attr['amount'])
            nameColor = self.data.qualityColor[self.attr['quality']]
            textWidth, textHeight = self.fonts[15].size(self.attr['name'] + ' ' + amount)
            self.drawText(
                surface=self.surface, font=self.fonts[15], text=self.attr['name'] + ' ' + amount, 
                color=nameColor, x=x+self.imageSize[self.location][0]/2-textWidth/2, y=y-textHeight, alpha=255
            )
        else:
            self.surface.blit(self.qualityBg, (x, y))
        self.rect = pg.Rect(x, y, self.imageSize[self.location][0], self.imageSize[self.location][1])
        self.surface.blit(self.img, (x, y))

    def recycle(self):
        for i, r in enumerate(self.resources):
            if self.data.playerSave['money'+str(i)] < self.data.gameAttrRange['user money range'][1]:
                self.data.playerSave['money'+str(i)] += r
                if self.data.playerSave['money'+str(i)] > self.data.gameAttrRange['user money range'][1]:
                    self.data.playerSave['money'+str(i)] = self.data.gameAttrRange['user money range'][1]

    def upgradeLevel(self):
        successChance = round((1 - self.attr['level']/self.data.gameAttrRange['item level range'][1]), 2)
        successChance = 0.5 if successChance < 0.5 else successChance
        success = self.isHappening(chance=successChance)
        if success:
            self.attr['level'] += 1
            self.calculateAttr()
        return success

    def upgradeStar(self):
        successChance = round((1 - self.attr['icon star']/self.data.gameAttrRange['item star range'][1]), 2)
        successChance = 0.25 if successChance < 0.25 else successChance
        success = self.isHappening(chance=successChance)
        if success:
            self.attr['icon star'] += 1
            self.calculateAttr()
        return success

    def update(self):
        super().update()
        if self.eventInput['MOUSE_BUTTON_UP'] == 1:
            self.displayAttributes = True
        self.drawItem()