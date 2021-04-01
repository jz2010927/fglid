 # -*- coding: utf-8 -*-
from GameObject import GameObject
from Questions import Questions
import pygame as pg, random

class InBuildingScreen(GameObject):
    def __init__(self, data, surface, camera):
        super().__init__(data, surface, camera)
        self.menu = (self.showMain, self.dimensionJump, self.recycle, self.itemLevelUpgrade, self.itemStarUpgrade, self.study, self.gamble, self.submitCard)
        self.menuIndex = 0
        self.menuWidth, self.menuHeight = 800, 600
        self.menuX, self.menuY = self.width/2-self.menuWidth/2, self.height/2-self.menuHeight/2
        self.buttonWidth, self.buttonHeight = 150, 90
        self.tempText, self.tempTextColor, self.tempFontSize = '', self.colors['黑'], 20
        self.bet, self.gambleStartMoney, self.gambleTimer = 0, 0, 0
        self.betOddEven, self.gambleTimerCounting = None, True # 0 even, 1 odd
        self.betsClear, self.gambleStartMoneyNoted = False, False
        self.questions = Questions(data=self.data, surface=self.surface)
        self.currentQuestion, self.startedQuestion = None, False
        self.afterQuestionText = ''
        self.tColor = self.colors['黑']
        self.q_string, self.answers = '', []

    def updateVars(self):
        super().updateVars()
        self.menuIndex = 0
        self.tempText, self.tempTextColor, self.tempFontSize = '', self.colors['黑'], 20
        self.bet, self.gambleStartMoney, self.gambleTimer = 0, 0, 0
        self.betOddEven, self.gambleTimerCounting = None, True # 0 even, 1 odd
        self.betsClear, self.gambleStartMoneyNoted = False, False
        self.currentQuestion, self.startedQuestion = None, False
        self.afterQuestionText = ''
        self.q_string, self.answers = '', []
    
    def bottomButtons(self):
        gridEmpty_check = (
            self.data.mainbaseItem['recycle'] == None, 
            self.data.mainbaseItem['level upgrade'] == None, 
            self.data.mainbaseItem['star upgrade'] == None
        )
        quit = self.drawButton(
            surface=self.surface, x=self.menuX+20, y=self.menuY+self.menuHeight-self.buttonHeight-20, 
            width=self.buttonWidth, height=self.buttonHeight, 
            depth=3, text=self.data.language['quit'], 
            shading=True
        )
        if quit and all(gridEmpty_check):
            self.menuIndex = 0
            self.tempText, self.tempTextColor, self.tempFontSize = '', self.colors['黑'], 20
            self.bet, self.gambleStartMoney, self.gambleTimer = 0, 0, 0
            self.betOddEven, self.gambleTimerCounting = None, True # 0 even, 1 odd
            self.betsClear, self.gambleStartMoneyNoted = False, False
            self.currentQuestion, self.startedQuestion = None, False
            self.afterQuestionText = ''
            self.q_string, self.answers = '', []
            return False
        if self.menuIndex != 0:
            back = self.drawButton(
                surface=self.surface, x=self.menuX+self.menuWidth-self.buttonWidth-20, y=self.menuY+self.menuHeight-self.buttonHeight-20, 
                width=self.buttonWidth, height=self.buttonHeight, 
                depth=3, text=self.data.language['back'], 
                shading=True
            )
            if back and all(gridEmpty_check):
                self.tempText, self.tempTextColor, self.tempFontSize = '', self.colors['黑'], 20
                self.bet, self.gambleStartMoney, self.gambleTimer = 0, 0, 0
                self.betOddEven, self.gambleTimerCounting = None, True # 0 even, 1 odd
                self.betsClear, self.gambleStartMoneyNoted = False, False
                self.currentQuestion, self.startedQuestion = None, False
                self.afterQuestionText = ''
                self.q_string, self.answers = '', []
                self.menuIndex = 0
        return True

    def itemGrid(self, k):
        width, height = 33, 33
        x, y = self.menuX + self.menuWidth/2 - width/2, self.menuY + 100
        self.drawShading(surface=self.surface, coordinates=(x, y, width, height), lineSize=3, pressed=True)
        gridRect = pg.Rect(x, y, width, height)
        conditions = (
            gridRect.collidepoint(pg.mouse.get_pos()), 
            pg.mouse.get_pressed()[0] == 1, 
            self.data.holdingItem == None or self.data.holdingItem.attr['type'] == 0
        )
        if all(conditions):
            self.data.sounds['click 1'].play()
            temp = self.data.mainbaseItem[k]
            self.data.mainbaseItem[k] = self.data.holdingItem
            self.data.holdingItem = temp
            self.tempText, self.tempTextColor, self.tempFontSize = '', self.colors['黑'], 20
            pg.time.wait(250)
        if self.data.mainbaseItem[k] != None:
            self.data.mainbaseItem[k].x, self.data.mainbaseItem[k].y = x, y
            self.data.mainbaseItem[k].update()
            self.data.mainbaseItem[k].displayAttrHelper()
        text = self.data.language['remove item before exit']
        textWidth, textHeight = self.fonts[20].size(text)
        self.drawText(
            font=self.fonts[20], text=text, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+self.menuHeight-100, 
            surface=self.surface, alpha=255
        )

    def displayMoneyRequired(self, k, buttonName, conditionMust, conditionMustText):
        if k == None:
            moneyRequired = (
                # 木材
                int(1.023**(self.data.playerSave['main base level']+1)),
                # 合金 
                int(1.023**(self.data.playerSave['main base level']+1)), 
                # 净水
                int(1.021**(self.data.playerSave['main base level']+1)), 
                # 食物
                int(1.021**(self.data.playerSave['main base level']+1)), 
                # 燃料
                int(1.022**(self.data.playerSave['main base level']+1)), 
                # 金条
                int((self.data.playerSave['main base level']+1) ** 1.5)
            )
        else:
            moneyRequired = self.data.mainbaseItem[k].moneyRequired[k]
        # 条件1 资源
        condition1 = (
            # 木材
            self.data.playerSave['money0'] >= moneyRequired[0], 
            # 合金
            self.data.playerSave['money1'] >= moneyRequired[1], 
            # 净水
            self.data.playerSave['money2'] >= moneyRequired[2], 
            # 食物
            self.data.playerSave['money3'] >= moneyRequired[3], 
            # 燃料
            self.data.playerSave['money4'] >= moneyRequired[4], 
        )
        # 条件2 金条
        condition2 = [self.data.playerSave['moneyVIP'] >= moneyRequired[5]]
        # 显示必须条件
        for i, text in enumerate(conditionMustText):
            textWidth, textlHeight = self.fonts[20].size(text)
            textColor = self.colors['绿3'] if conditionMust[i] else self.colors['红']
            self.drawText(
                font=self.fonts[20], text=text, 
                color=textColor, x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+70+i*20, 
                surface=self.surface, alpha=255
            )
        # 显示条件1
        condition1Names = ( 
            self.data.language['money0'], self.data.language['money1'], self.data.language['money2'], 
            self.data.language['money3'], self.data.language['money4'], 
        )
        for i, condition in enumerate(condition1):
            text = self.data.language['need'] + ' ' + condition1Names[i] + ': ' + str(self.data.playerSave['money'+str(i)]) + '/' + str(moneyRequired[i])
            textColor = self.colors['绿3'] if condition else self.colors['红']
            textWidth, textHeight = self.fonts[20].size(text)
            self.drawText(
                font=self.fonts[20], text=text, 
                color=textColor, x=self.menuX+20, y=self.menuY+150+50*i, 
                surface=self.surface, alpha=255
            )
        # 显示条件2
        condition2Name = self.data.language['moneyVIP']
        condition2Text = self.data.language['need'] + ' ' + condition2Name + ': ' + str(self.data.playerSave['moneyVIP']) + '/' + str(moneyRequired[5])
        textWidth, textHeight = self.fonts[20].size(condition2Text)
        textColor = self.colors['绿3'] if condition2[0] else self.colors['红']
        self.drawText(
            font=self.fonts[20], text=condition2Text, 
            color=textColor, x=self.menuX+self.menuWidth-self.buttonWidth-150, y=self.menuY+self.height//3-20, 
            surface=self.surface, alpha=255
        )
        # 显示 或
        orTextWidth, orTextHeight = self.fonts[50].size(self.data.language['or'])
        self.drawText(
            font=self.fonts[50], text=self.data.language['or'], 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-orTextWidth/2, y=self.menuY+self.height//3-orTextHeight, 
            surface=self.surface, alpha=255
        )
        # 条件1成立显示条件1按钮
        buttonLeftClicked, buttonRightClicked = False, False
        if all(condition1) and all(conditionMust):
            buttonLeftClicked = self.drawButton(
                    surface=self.surface, x=self.menuX+100, y=self.menuY+self.menuHeight-self.buttonHeight*2-20, 
                    width=100, height=62, 
                    depth=3, text=buttonName, 
                    shading=True
            )
        # 条件2成立显示条件2按钮
        if all(condition2) and all(conditionMust):
            buttonRightClicked = self.drawButton(
                    surface=self.surface, x=self.menuX+self.menuWidth-self.buttonWidth-100, y=self.menuY+self.menuHeight-self.buttonHeight*2-20, 
                    width=100, height=62, 
                    depth=3, text=buttonName, 
                    shading=True
            )

        return moneyRequired, buttonLeftClicked, buttonRightClicked


    def displayItemNum(self, keyWord):
        # 确定数值
        imgSize = (64, 64)
        imgX, imgY = self.menuX+self.menuWidth-200, self.menuY+50
        # 显示名称
        try:
            self.drawText(
                font=self.fonts[20], text=self.data.language[keyWord], 
                color=self.colors['黑'], x=imgX, y=imgY-25, 
                surface=self.surface, alpha=255
            )
        except:
            print(keyWord)
        # 数数
        n = self.data.countItemInBag(keyWord=keyWord)
        # 显示icon
        img = pg.transform.scale(self.data.images[keyWord].convert_alpha(), imgSize)
        self.surface.blit(img, (imgX, imgY))
        # 显示数量
        text = ' x ' + str(n)
        self.drawText(
            font=self.fonts[40], text=text, 
            color=self.colors['黑'], x=imgX+imgSize[0]+10, y=imgY+5, 
            surface=self.surface, alpha=255
        )
        return n

    def showMain(self):
        textMainbaseLevel = self.data.language['current'] + ' ' + self.data.language['dimension'] + ': ' + str(self.data.playerSave['main base level']) + '/' + str(self.data.gameAttrRange['main base level range'][1])
        textMainbaseLevelWidth, textMainbaseLevelHeight = self.fonts[20].size(textMainbaseLevel)
        self.drawText(
            font=self.fonts[20], text=textMainbaseLevel, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textMainbaseLevelWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        buttonkeyWords = (
            'dimension jump', 'recycle', 'item upgrade level', 
            'item upgrade star', 'skill levelup', 'gamble'
        )
        offsetX = 50
        buttonX = self.menuX + offsetX
        for i, k in enumerate(buttonkeyWords):
            text = self.data.language[k]
            if k == 'gamble':
                text = self.data.language['moneyVIP'] + ' ' + self.data.language[k]
            isClicked = self.drawButton(
                    surface=self.surface, x=buttonX, y=self.menuY+100+(self.buttonHeight+20)*(i//2), 
                    width=self.buttonWidth, height=self.buttonHeight, 
                    depth=3, text=text, 
                    shading=True
                )
            if isClicked:
                self.menuIndex = i + 1
            buttonX = self.menuX+self.menuWidth-self.buttonWidth-offsetX if buttonX == self.menuX+offsetX else self.menuX+offsetX
        submitCard = self.drawButton(
                    surface=self.surface, x=self.width/2-self.buttonWidth/2, y=self.menuY+100+(self.buttonHeight+20), 
                    width=self.buttonWidth, height=self.buttonHeight, 
                    depth=3, text=self.data.language['submit'] + ' ' + self.data.language['poker card'], 
                    shading=True
                )
        if submitCard:
            self.menuIndex = -1
    
    def submitCard(self):
        titleText = self.data.language['submit'] + ' ' + self.data.language['poker card']
        titleTextWidth, titleTextHeight = self.fonts[20].size(titleText)
        self.drawText(
            font=self.fonts[20], text=titleText, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-titleTextWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        titleText2 = self.data.language['poker deck use condition']
        titleText2Width, titleText2Height = self.fonts[20].size(titleText2)
        self.drawText(
            font=self.fonts[20], text=titleText2, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-titleText2Width/2, y=self.menuY+titleText2Height+20, 
            surface=self.surface, alpha=255
        )
        # 显示牌个数
        cardSuits = ('H', 'S', 'C', 'D')
        cardKey_Jokers = ('card_smallJoker', 'card_bigJoker')
        cardKey_suit = {'H': 'poker heart', 'S': 'poker spade', 'C': 'poker club', 'D': 'poker diamond'}
        cardKey_Num = ['card_0'+str(i) for i in range(1, 10)] + ['card_'+str(i) for i in range(10, 14)]
        cardName_Num = {k:str(int(k[-2:])) for k in cardKey_Num}
        cardName_Num['card_01'] = 'A'
        cardName_Num['card_11'] = 'J'
        cardName_Num['card_12'] = 'Q'
        cardName_Num['card_13'] = 'K'
        font_size = 20
        # 显示大小王
        for i, k in enumerate(cardKey_Jokers):
            try:
                text = self.data.language[k]+': '+str(self.data.playerSave['cards'][k])
                textWidth, textHeight = self.fonts[font_size].size(text)
                x = self.menuX+100 if i == 0 else self.menuX+self.menuWidth-textWidth-100
                self.drawText(
                    font=self.fonts[font_size], text=text, 
                    color=self.colors['黑'], x=x, y=self.menuY+70, 
                    surface=self.surface, alpha=255
                )
            except:
                print(k, ' self.data.language[k]: ', self.data.language[k])
                print(k, ' self.data.playerSave[cards][k]: ', self.data.playerSave['cards'][k])
        # 显示其他牌
        for i, suit in enumerate(cardSuits):
            language_k = self.data.language[cardKey_suit[suit]]
            for j, num in enumerate(cardKey_Num):
                card_name = cardName_Num[num]
                text = language_k + ' ' + card_name + ': ' + str(self.data.playerSave['cards'][num+suit])
                textWidth, textHeight = self.fonts[font_size].size(text)
                self.drawText(
                    font=self.fonts[font_size], text=text, 
                    color=self.colors['黑'], x=self.menuX+50+185*i, y=self.menuY+90+25*j, 
                    surface=self.surface, alpha=255
                )
        # 显示一共凑齐几副牌
        text = self.data.language['deck'] + ': ' + str(min(tuple(self.data.playerSave['cards'].values())))
        textWidth, textHeight = self.fonts[font_size].size(text)
        self.drawText(
                    font=self.fonts[font_size], text=text, 
                    color=self.colors['黑'], x=self.width/2-textWidth/2, y=self.menuY+self.menuHeight-self.buttonHeight-50, 
                    surface=self.surface, alpha=255
                )
        # 提交按钮
        submitCard = self.drawButton(
                    surface=self.surface, x=self.width/2-self.buttonWidth/2, y=self.menuY+self.menuHeight-self.buttonHeight-20, 
                    width=self.buttonWidth, height=self.buttonHeight, 
                    depth=3, text=self.data.language['submit'], 
                    shading=True
                )
        if submitCard:
            for page in range(len(self.data.playerSave['backpack'])):
                for index in range(len(self.data.playerSave['backpack'][page])):
                    conditions = (
                        self.data.playerSave['backpack'][page][index] == None, 
                        self.data.playerSave['backpack'][page][index] == 'occupied'
                    )
                    if any(conditions):
                        continue
                    k = self.data.playerSave['backpack'][page][index]['key word']
                    if 'card_' in k:
                        self.data.playerSave['cards'][k] += 1
                        self.data.playerSave['backpack'][page][index] = None

    def dimensionJump(self):
        titleText = self.data.language['dimension jump']
        titleTextWidth, titleTextHeight = self.fonts[20].size(titleText)
        self.drawText(
            font=self.fonts[20], text=titleText, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-100, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        nextLevelText = self.data.language['next level'] + ': ' + str(self.data.playerSave['main base level']) + ' --> ' + str(self.data.playerSave['main base level']+1)
        self.drawText(
            font=self.fonts[20], text=nextLevelText, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2+titleTextWidth-50, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        conditionMust = [
            # 知识水平要大于等于下一级维度等级
            self.data.playerSave['knowledge level'] >= self.data.playerSave['main base level'], 
            # 玩家等级要大于等于下一级维度等级
            self.data.playerSave['level'] >= self.data.playerSave['main base level']
        ]
        conditionMustNames = (self.data.language['knowledge level'], self.data.language['user level'], self.data.language['poker card']+' '+self.data.language['deck'])
        conditionMustText0 = self.data.language['need'] + ' ' + conditionMustNames[0] + ': ' + str(self.data.playerSave['knowledge level']) + '/' + str(self.data.playerSave['main base level'])
        conditionMustText1 = self.data.language['need'] + ' ' + conditionMustNames[1] + ': ' + str(self.data.playerSave['level']) + '/' + str(self.data.playerSave['main base level'])
        conditionMustTexts = [conditionMustText0, conditionMustText1]
        if self.data.playerSave['main base level'] >= 900:
            conditionMust.append((min(tuple(self.data.playerSave['cards'].values())) > 0))
            conditionMustText2 = self.data.language['need'] + ' ' + conditionMustNames[2] + ': ' + str(min(tuple(self.data.playerSave['cards'].values()))) + '/' + '1'
            conditionMustTexts.append(conditionMustText2)
        moneyRequire, btnLeft, btnRight = self.displayMoneyRequired(
            k=None, buttonName=self.data.language['jump'], conditionMust=conditionMust, conditionMustText=conditionMustTexts
        )
        # 如果按钮按下
        if btnLeft or btnRight:
            self.data.sounds['glass break'].play()
            if self.data.playerSave['main base level'] <= self.data.gameAttrRange['main base level range'][1]:
                self.data.playerSave['main base level'] += 1
                if self.data.playerSave['main base level'] >= 900:
                    for k in self.data.playerSave['cards'].keys():
                        self.data.playerSave['cards'][k] -= 1
                if btnLeft:
                    for i in range(5):
                        self.data.playerSave['money'+str(i)] -= moneyRequire[i]
                if btnRight:
                    self.data.playerSave['moneyVIP'] -= moneyRequire[5]

    def recycle(self):
        text = self.data.language['recycle']
        textWidth, textlHeight = self.fonts[20].size(text)
        self.drawText(
            font=self.fonts[20], text=text, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        if self.data.mainbaseItem['recycle'] != None:
            resources = self.data.mainbaseItem['recycle'].resources
            resourceImgs = [pg.transform.scale(img, (32, 32)) for k, img in self.data.moneyImgs.items() if 'VIP' not in k]
            recycle_btn = self.drawButton(
                    surface=self.surface, x=self.menuX+self.menuWidth/2-self.buttonWidth/2, y=self.menuY+self.menuHeight-self.buttonHeight*2-20, 
                    width=100, height=62, 
                    depth=3, text=self.data.language['recycle'], 
                    shading=True
            )
            for i, r in enumerate(resources):
                x, y = self.menuX+self.menuWidth/2-100, self.menuY+150+40*i
                self.surface.blit(resourceImgs[i], (x, y))
                self.drawText(
                    font=self.fonts[20], text=' x ' + str(r), 
                    color=self.colors['黑'], x=x+100, y=y, 
                    surface=self.surface, alpha=255
                )      
                if recycle_btn:
                    self.data.playerSave['money'+str(i)] = self.addValueWithLimit(value=self.data.playerSave['money'+str(i)], addNum=r, limit=self.data.gameAttrRange['user money range'][1])
            if recycle_btn:
                self.data.sounds['coin drop'].play()
                self.data.mainbaseItem['recycle'] = None
        # 物品放置格子
        self.itemGrid(k='recycle')


    def itemLevelUpgrade(self):
        # 升级保护数量
        protectorNum = self.displayItemNum(keyWord='consumable doge')
        text = self.data.language['item upgrade level']
        textWidth, textHeight = self.fonts[20].size(text)
        self.drawText(
            font=self.fonts[20], text=text, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        if self.data.mainbaseItem['level upgrade'] != None:
            # 前置条件
            conditionMust = (
                # 玩家等级要大于等于物品星级*100
                self.data.playerSave['level'] >= self.data.mainbaseItem['level upgrade'].attr['level'], 
            )
            conditionMustName = self.data.language['user level']
            conditionMustText = self.data.language['need'] + ' ' + conditionMustName + ': ' + str(self.data.playerSave['level']) + '/' + str(self.data.mainbaseItem['level upgrade'].attr['level'])
            moneyRequire, btnLeft, btnRight = self.displayMoneyRequired(
                k='level upgrade', buttonName=self.data.language['upgrade'], conditionMust=conditionMust, conditionMustText=(conditionMustText, )
            )
            # 如果按钮按下
            if btnLeft or btnRight:
                self.data.sounds['forge 1'].play()
                if self.data.mainbaseItem['level upgrade'].attr['level'] < self.data.gameAttrRange['item level range'][1]:
                    success = self.data.mainbaseItem['level upgrade'].upgradeLevel()
                    if not success:
                        if protectorNum > 0:
                            self.data.deleteItemFromBag(keyWord='consumable doge', maxNum=1)
                        else:
                            self.data.mainbaseItem['level upgrade'].attr['level'] = self.minusValueWithLimit(value=self.data.mainbaseItem['level upgrade'].attr['level'],minusNum=1,limit=0)
                    self.data.mainbaseItem['level upgrade'].updateVars()
                    if btnLeft:
                        for i in range(5):
                            self.data.playerSave['money'+str(i)] -= moneyRequire[i]
                    if btnRight:
                        self.data.playerSave['moneyVIP'] -= moneyRequire[5]
                    self.tempText = self.data.language['success'] if success else self.data.language['fail']
                    self.tempTextColor = self.colors['金'] if success else self.colors['灰']
                    self.tempFontSize = 40 if success else 20
            self.drawText(
                font=self.fonts[self.tempFontSize], text=self.tempText, 
                color=self.tempTextColor, x=self.menuX+self.menuWidth/2+100, y=self.menuY+200, 
                surface=self.surface, alpha=255
            )
        # 物品放置格子
        self.itemGrid(k='level upgrade')


    def itemStarUpgrade(self):
        # 升级保护数量
        protectorNum = self.displayItemNum(keyWord='consumable doge')
        text = self.data.language['item upgrade star']
        textWidth, textHeight = self.fonts[20].size(text)
        self.drawText(
            font=self.fonts[20], text=text, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        if self.data.mainbaseItem['star upgrade'] != None:
            # 前置条件
            levelRequire = (self.data.mainbaseItem['star upgrade'].attr['icon star']+1)*100 + 1
            conditionMust = (
                # 玩家等级要大于等于物品星级*100
                self.data.playerSave['level'] >= levelRequire, 
            )
            conditionMustName = self.data.language['user level']
            conditionMustText = self.data.language['need'] + ' ' + conditionMustName + ': ' + str(self.data.playerSave['level']) + '/' + str(levelRequire)
            moneyRequire, btnLeft, btnRight = self.displayMoneyRequired(
                k='star upgrade', buttonName=self.data.language['upgrade'], conditionMust=conditionMust, conditionMustText=(conditionMustText, )
            )
            # 如果按钮按下
            if btnLeft or btnRight:
                self.data.sounds['forge 0'].play()
                if self.data.mainbaseItem['star upgrade'].attr['icon star'] < self.data.gameAttrRange['item star range'][1]:
                    success = self.data.mainbaseItem['star upgrade'].upgradeStar()
                    if not success:
                        if protectorNum > 0:
                            self.data.deleteItemFromBag(keyWord='consumable doge', maxNum=1)
                        else:
                            self.data.mainbaseItem['star upgrade'].attr['star'] = self.minusValueWithLimit(value=self.data.mainbaseItem['star upgrade'].attr['star'],minusNum=1,limit=0)
                    self.data.mainbaseItem['star upgrade'].updateVars()
                    if btnLeft:
                        for i in range(5):
                            self.data.playerSave['money'+str(i)] -= moneyRequire[i]
                    if btnRight:
                        self.data.playerSave['moneyVIP'] -= moneyRequire[5]
                    self.tempText = self.data.language['success'] if success else self.data.language['fail']
                    self.tempTextColor = self.colors['金'] if success else self.colors['灰']
                    self.tempFontSize = 40 if success else 20
            self.drawText(
                font=self.fonts[self.tempFontSize], text=self.tempText, 
                color=self.tempTextColor, x=self.menuX+self.menuWidth/2+100, y=self.menuY+200, 
                surface=self.surface, alpha=255
            )
        # 物品放置格子
        self.itemGrid(k='star upgrade')
    
    def study(self):
        # 答题卡数量
        answerSheetNum = self.displayItemNum(keyWord='consumable answer sheet')
        # 显示标题
        text = self.data.language['skill levelup']
        textWidth, textHeight = self.fonts[20].size(text)
        self.drawText(
            font=self.fonts[20], text=text, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        # 确定升级所需经验
        self.data.playerSave['knowledge levelup exp'] = self.data.playerSave['knowledge level'] + 1
        # 显示知识等级
        t = self.data.language['knowledge level']+': '+str(self.data.playerSave['knowledge level'])+'      '+self.data.language['exp']+': '+str(self.data.playerSave['knowledge exp'])+'/'+str(self.data.playerSave['knowledge levelup exp'])
        tWidth, tHeight = self.fonts[20].size(t)
        self.drawText(
            font=self.fonts[20], text=t, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-tWidth/2, y=self.menuY+50, 
            surface=self.surface, alpha=255
        )
        # 显示金条数量
        self.drawText(
            font=self.fonts[20], text=self.data.language['current']+' '+self.data.language['moneyVIP']+': '+str(self.data.playerSave['moneyVIP']), 
            color=self.colors['金2'], x=self.menuX+self.menuWidth/2-tWidth/2, y=self.menuY+70, 
            surface=self.surface, alpha=255
        )
        # 金条奖励
        moneyVIP_reward = 50
        # 选项前缀
        optionPrefix = ('A', 'B', 'C', 'D')
        # 获取题目
        if answerSheetNum > 0:
            startAnswerButtonText = self.data.language['change question'] if self.startedQuestion else self.data.language['start answer question']
            startAnswer = self.drawButton(
                    surface=self.surface, 
                    x=self.menuX+self.menuWidth/2-50, 
                    y=self.menuY+self.menuHeight-100, 
                    width=100, height=62, 
                    depth=3, text=startAnswerButtonText, 
                    shading=True
                )
            if startAnswer:
                self.startedQuestion = True
                self.questions.symbolUsed = set()
                self.currentQuestion = self.questions.randomQuestion()
                # 用掉一张答题卡
                self.data.deleteItemFromBag(keyWord='consumable answer sheet', maxNum=1)
                self.q_string =self.currentQuestion['Q']
                self.answers = [
                    self.currentQuestion['A'], 
                    *self.currentQuestion['W_As']
                ]
                random.shuffle(self.answers)
        if self.currentQuestion != None:
            # 渲染问题
            questionWidth, questionHeight = self.fonts[30].size(self.q_string)
            self.drawText(
                font=self.fonts[20], text=self.q_string, 
                color=self.colors['黑'], x=self.menuX+120, y=self.menuY+self.menuHeight/2-170, 
                surface=self.surface, alpha=255
            )
            # 渲染答案以及按钮
            for i in range(4):
                self.drawText(
                    font=self.fonts[15], text=self.answers[i], 
                    color=self.colors['黑'], x=self.menuX+140, y=self.menuY+self.menuHeight/2-70+70*i, 
                    surface=self.surface, alpha=255
                )
                answerButton = self.drawButton(
                    surface=self.surface, 
                    x=self.menuX+20, 
                    y=self.menuY+self.menuHeight/2-100+70*i, 
                    width=100, height=62, 
                    depth=3, text=optionPrefix[i], 
                    shading=True
                )
                if answerButton:
                    self.startedQuestion = False
                    if self.answers[i] == self.currentQuestion['A']:
                        # 播放奖励声音
                        self.data.sounds['ding'].play()
                        # 获取经验
                        if self.data.playerSave['knowledge level'] < self.data.gameAttrRange['main base level range'][1]:
                            self.data.playerSave['knowledge exp'] += 1
                            if self.data.playerSave['knowledge exp'] >= self.data.playerSave['knowledge levelup exp']:
                                self.data.playerSave['knowledge level'] += 1
                                self.data.playerSave['knowledge exp'] = 0
                        # 获取金条奖励
                        self.data.playerSave['moneyVIP'] = self.addValueWithLimit(value=self.data.playerSave['moneyVIP'], addNum=moneyVIP_reward, limit=self.data.gameAttrRange['user money range'][1])
                        # 显示奖励
                        self.afterQuestionText = self.data.language['correct'] + ' ' + self.data.language['knowledge exp'] + '+1, ' + self.data.language['moneyVIP'] + '+' + str(moneyVIP_reward)
                        self.tColor = self.colors['金2']
                    else:
                        self.data.sounds['wrong'].play()
                        self.afterQuestionText = self.data.language['wrong']
                        self.tColor = self.colors['黑']
                    # 清空问题
                    self.currentQuestion = None
        # 显示回答正确或错误, 以及奖励
        if self.currentQuestion == None:
            t = self.afterQuestionText
            tWidth, tHeight = self.fonts[30].size(t)
            self.drawText(
                font=self.fonts[30], text=t, 
                color=self.tColor, x=self.menuX+self.menuWidth/2-tWidth/2, y=self.menuY+self.menuHeight/2-tHeight/2, 
                surface=self.surface, alpha=255
            )

    def gamble(self):
        if not self.gambleStartMoneyNoted:
            self.gambleStartMoney = self.data.playerSave['moneyVIP']
            self.gambleStartMoneyNoted = True
        # title
        textTitle = self.data.language['gamble'] + '(' + self.data.language['gamble collection'] + ')'
        textWidth, textHeight = self.fonts[20].size(textTitle)
        self.drawText(
            font=self.fonts[20], text=textTitle, 
            color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+20, 
            surface=self.surface, alpha=255
        )
        winMoney = self.data.playerSave['moneyVIP'] - self.gambleStartMoney
        text = self.data.language['win'] if winMoney >= 0 else self.data.language['lose']
        textColor = self.colors['红'] if winMoney >= 0 else self.colors['黑']
        textWidth, textHeight = self.fonts[20].size(text+' '+str(abs(winMoney)))
        self.drawText(
            font=self.fonts[20], text=text+' '+str(abs(winMoney)), 
            color=textColor, x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+50, 
            surface=self.surface, alpha=255
        )
        if self.data.playerSave['moneyVIP'] < 50 and self.gambleTimerCounting:
            textWidth, textHeight = self.fonts[20].size(self.data.language['not enough bullion'])
            self.drawText(
                font=self.fonts[20], text=self.data.language['not enough bullion'], 
                color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+100, 
                surface=self.surface, alpha=255
            )
        #  押注按钮
        if self.bet == 0:
            bets = (50, 100, 500)
            for i, bet in enumerate(bets):
                if self.data.playerSave['moneyVIP'] >= bet:
                    betButton = self.drawButton(
                        surface=self.surface, x=self.menuX+90+(self.menuWidth//3)*i, y=self.menuY+self.menuHeight-self.buttonHeight*2, 
                        width=100, height=62, 
                        depth=3, text=self.data.language['bet']+' '+str(bet), 
                        shading=True
                    )
                    if betButton:
                        self.bet = bet
        if self.bet > 0:
            textWidth, textHeight = self.fonts[20].size(self.data.language['bet']+': '+str(self.bet))
            self.drawText(
                font=self.fonts[20], text=self.data.language['bet']+': '+str(self.bet), 
                color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+self.menuHeight-self.buttonHeight*2-40, 
                surface=self.surface, alpha=255
            )
            if self.betOddEven == None:
                # 显示玩法
                textWidth, textHeight = self.fonts[20].size(self.data.language['gamble introduction'])
                self.drawText(
                    font=self.fonts[20], text=self.data.language['gamble introduction'], 
                    color=self.colors['黑'], x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+self.menuHeight/2, 
                    surface=self.surface, alpha=255
                )
                # 选奇偶
                oddButton = self.drawButton(
                        surface=self.surface, x=self.menuX+self.menuWidth/2-200, y=self.menuY+self.menuHeight-self.buttonHeight, 
                        width=100, height=62, 
                        depth=3, text=self.data.language['odd'], 
                        shading=True
                    )
                evenButton = self.drawButton(
                        surface=self.surface, x=self.menuX+self.menuWidth/2+100, y=self.menuY+self.menuHeight-self.buttonHeight, 
                        width=100, height=62, 
                        depth=3, text=self.data.language['even'], 
                        shading=True
                    )
                if oddButton:
                    self.betOddEven = 1
                if evenButton:
                    self.betOddEven = 0
            else:
                # 计数器
                timerTextWidth, timerTextHeight = self.fonts2[55].size(str(self.gambleTimer))
                self.drawText(
                    font=self.fonts2[55], text=str(self.gambleTimer), 
                    color=self.colors['黑'], x=self.menuX+self.menuWidth/2-timerTextWidth/2, y=self.menuY+self.menuHeight/2-timerTextHeight/2, 
                    surface=self.surface, alpha=255
                )
                if self.gambleTimerCounting:
                    self.gambleTimer = random.randint(0, 10000)
                if self.gambleTimerCounting:
                    stopTimer = self.drawButton(
                            surface=self.surface, x=self.width/2-self.buttonWidth/2, y=self.menuY+self.menuHeight-self.buttonHeight-20, 
                            width=self.buttonWidth, height=self.buttonHeight, 
                            depth=3, text=self.data.language['stop'], 
                            shading=True
                        )
                    if stopTimer:
                        self.gambleTimerCounting = False
                if not self.gambleTimerCounting:
                    text = self.data.language['win']
                    color=self.colors['红']
                    if self.gambleTimer & 1 == self.betOddEven:
                        if not self.betsClear:
                            self.data.playerSave['moneyVIP'] = self.addValueWithLimit(value=self.data.playerSave['moneyVIP'], addNum=int(self.bet * 0.95), limit=self.data.gameAttrRange['user money range'][1])
                    else:
                        text = self.data.language['lose']
                        color=self.colors['黑']
                        if not self.betsClear:
                            self.data.playerSave['moneyVIP'] = self.minusValueWithLimit(value=self.data.playerSave['moneyVIP'], minusNum=self.bet, limit=self.data.gameAttrRange['user money range'][0])
                    textWidth, textHeight = self.fonts[71].size(text)
                    self.drawText(
                            font=self.fonts[71], text=text, 
                            color=color, x=self.menuX+self.menuWidth/2-textWidth/2, y=self.menuY+self.menuHeight/2-200, 
                            surface=self.surface, alpha=255
                        )
                    self.betsClear = True
                    oneMore = self.drawButton(
                            surface=self.surface, x=self.width/2-50, y=self.menuY+self.menuHeight-self.buttonHeight*2-50, 
                            width=100, height=62, 
                            depth=3, text=self.data.language['restart'], 
                            shading=True
                        )
                    if oneMore:
                        self.bet, self.gambleTimer = 0, 0
                        self.betOddEven, self.gambleTimerCounting = None, True # 0 even, 1 odd
                        self.betsClear = False

                    

    def update(self):
        super().update()
        self.menuX, self.menuY = self.width/2-self.menuWidth/2, self.height/2-self.menuHeight/2
        # 背景
        pg.draw.rect(self.surface, self.colors['绿2'], (self.menuX, self.menuY, self.menuWidth, self.menuHeight))
        # 底部按钮
        display = self.bottomButtons()
        # 菜单
        self.menu[self.menuIndex]()
        if not display:
            self.changeScene = True
        return display
