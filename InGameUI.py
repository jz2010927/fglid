 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, re, copy
from Player import Player
from Item import Item

class InGameUI(GameBase):
    def __init__(self, data, surface, camera, player):
        super().__init__(data, surface)
        self.id = 6
        self.backpackImg, self.playerAttrImg = self.data.images['inventory ui'].convert_alpha(), self.data.images['attributes ui'].convert_alpha()
        self.leftArrow, self.leftArrowClicked = self.data.images['left arrow'].convert_alpha(), self.data.images['left arrow clicked'].convert_alpha()
        self.showBackpack, self.showPlayerAttr = False, False
        self.showInGameOption, self.showSaveLoadMenu = False, False
        self.selectedItem = -1
        self.backpackPage = 0
        self.userInput, self.insertPosMark = '', '|'
        self.shortKey = True
        self.camera = camera
        self.player = player
        
    def updateVars(self):
        super().updateVars()
        self.showBackpack, self.showPlayerAttr = False, False
        self.showInGameOption, self.showSaveLoadMenu = False, False
        self.selectedItem = -1
        self.saveList = self.data.loadSaveList()

    def addCommaToInt(self, num: int, group=3, char=','):
        s = str(num)
        newStr = None
        length = len(s)
        if length <= group:
            newStr = s
        else:
            head = length % group
            if head == 0:
                newStr = char.join(s[i:i+group] for i in range(head, len(s), group))
            else:
                newStr = s[0:head]+char+char.join(s[i:i+group] for i in range(head, len(s), group))
        return newStr

    def userInputFileName(self):
        maxLength = 100
        if len(self.userInput) <= maxLength:
            if self.eventInput['KEY_UNICODE'] != None and re.search(r"\W", self.eventInput['KEY_UNICODE']) == None:
                self.userInput += self.eventInput['KEY_UNICODE']
            if pg.key.get_pressed()[pg.K_BACKSPACE]:
                if len(self.userInput) > 0:
                    self.userInput = self.userInput[:-1]
            if pg.key.get_pressed()[pg.K_DELETE]:
                if len(self.userInput) > 0:
                    self.userInput = self.userInput[1:]

    def drawInventory(self):
        # 显示拥有资源
        width = self.backpackImg.get_width()
        ui_x, ui_y = 20, 150
        self.surface.blit(self.backpackImg, (ui_x, ui_y))
        backpackTextWidth, backpackTextHeight = self.fonts[20].size(self.data.language['backpack'])
        self.drawText(
            font=self.fonts[20], text=self.data.language['backpack'], 
            color=self.colors['黑'], x=ui_x+width/2-backpackTextWidth/2-10, y=ui_y-25, 
            surface=self.surface, alpha=255
        )
        # 显示金钱数值
        moneyTypes = [self.addCommaToInt(num=self.data.playerSave['money'+str(i)]) for i in range(5)]
        moneyTypes.append(self.addCommaToInt(num=self.data.playerSave['moneyVIP']))
        for i, money in enumerate(moneyTypes):
            self.drawText(
                font=self.fonts[20], text=money, 
                color=self.colors['黑'], x=ui_x+60, y=ui_y+341+34*i, 
                surface=self.surface, alpha=255
            )
        # 显示排序按钮
        self.drawButton(
                surface=self.surface, x=ui_x+390, y=ui_y+340, 
                width=90, height=20, 
                depth=0, text=self.data.language['sort backpack'], 
                shading=False, transparent=True
            )
        buttonWidth, buttonHeight = 90, 40
        buttonOffsetX, buttonOffsetY = 390, 365
        keys = ('icon star', 'quality', 'level', 'name')
        for i, k in enumerate(keys):
            text = self.data.language[k]
            clicked = self.drawButton(
                surface=self.surface, x=ui_x+buttonOffsetX, y=ui_y+buttonOffsetY+45*i, 
                width=buttonWidth, height=buttonHeight, 
                depth=3, text=self.data.language['in order of']+' '+text, shading=True
            )
            if clicked:
                flat_list = [item for sublist in self.data.playerSave['backpack'] for item in sublist if item != None]
                flat_list = sorted(flat_list, key=lambda attr: attr[k], reverse=True)
                self.data.playerSave['backpack'] = copy.deepcopy(self.data.defaultPlayerSave['backpack'])
                for page in range(len(self.data.playerSave['backpack'])):
                    for i in range(len(self.data.playerSave['backpack'][page])):
                        try:
                            self.data.playerSave['backpack'][page][i] = flat_list[page*60+i]
                        except:
                            return
        # 陈列背包物品
        backpackItems = []
        topleftX, topleftY = 10, 38
        offsetX, offsetY = 49, 49
        for i, itemAttr in enumerate(self.data.playerSave['backpack'][self.backpackPage]):
            row = i // 10
            column = i % 10
            gridX, gridY = ui_x+topleftX+offsetX*column, ui_y+topleftY+offsetY*row
            # self.putdownHoldingItem(x=gridX, y=gridY, itemAttr=itemAttr, place='backpack', i=i)
            item = None
            if itemAttr != None:
                item = Item(data=self.data, surface=self.surface, camera=self.camera, attr=itemAttr)
                item.location = 'in backpack'
                item.x, item.y = gridX, gridY
                item.update()
                item.rightClick(i=i, page=self.backpackPage, player=self.player)
            gridRect = pg.Rect(gridX, gridY, 33, 33)
            if gridRect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0] == 1:
                self.data.sounds['click 1'].play()
                temp = self.data.holdingItem
                self.data.holdingItem = item
                item = temp
                self.data.playerSave['backpack'][self.backpackPage][i] = item.attr if item != None else None
                if self.data.playerSave['backpack'][self.backpackPage][i] != None:
                    self.data.playerChanged = True
                pg.time.wait(200)
            backpackItems.append(item)
        for item in backpackItems:
            if item != None:
                item.displayAttrHelper()
        # 显示翻页
        totalPageNum = len(self.data.playerSave['backpack'])
        self.leftArrow = pg.transform.scale(self.leftArrow, (16, 16))
        self.leftArrowClicked = pg.transform.scale(self.leftArrowClicked, (16, 16))
        pageSelectWidth = 200
        arrowX, arrowY = ui_x+(width-pageSelectWidth)/2-10, ui_y+10
        self.backpackPage = self.arrowSelect(
            surface=self.surface, x=arrowX, y=arrowY, width=pageSelectWidth, 
            leftArrowImg=self.leftArrow, clickedLeftArrowImg=self.leftArrowClicked, 
            currentIndex=self.backpackPage, listLength=totalPageNum
        )
        self.drawText(
            font=self.fonts[15], text=self.data.language['page']+': ', 
            color=self.colors['黑'], x=ui_x+(width-pageSelectWidth)/2-50, y=ui_y+10, 
            surface=self.surface, alpha=255
        )
        pageText = str(self.backpackPage+1) + '/' + str(totalPageNum)
        pageTextWidth, pageTextHeight = self.fonts[20].size(pageText)
        self.drawText(
            font=self.fonts[20], text=pageText, 
            color=self.colors['黑'], x=arrowX+pageSelectWidth/2-pageTextWidth/2, y=ui_y+7, 
            surface=self.surface, alpha=255
        )

    def drawPlayerAttr(self):
        # 显示人物属性
        width = self.playerAttrImg.get_width()
        ui_x, ui_y = self.width-width-20, 150
        self.surface.blit(self.playerAttrImg, (ui_x, ui_y))
        playerAttrTextWidth, playerAttrTextHeight = self.fonts[20].size(self.data.language['player attributes'])
        self.drawText(
            font=self.fonts[20], text=self.data.language['player attributes'], 
            color=self.colors['黑'], x=ui_x+width/2-playerAttrTextWidth/2-10, y=ui_y-25, 
            surface=self.surface, alpha=255
        )
        # 显示等级
        self.drawButton(
            surface=self.surface, x=ui_x+100, y=ui_y+30, 
            width=99, height=49, 
            depth=0, text=self.data.language['level']+'. '+str(self.data.playerSave['level']), 
            shading=False, transparent=True
        )
        # 显示属性
        texts = (
            'attack', 'defense', 'attack speed', 'move speed', 'hp recovery', 
            'critical chance', 'critical multiplier', 'dodge chance', 'attack range'
        )
        for i, text in enumerate(texts):
            value_str = str(self.data.playerTotalValues[text])
            if type(self.data.playerTotalValues[text]) == float:
                value_str = str(int(self.data.playerTotalValues[text]*100)) + '%'
            textDisplay = self.data.language[text]+'   '+value_str
            if text == 'hp recovery':
                textDisplay = textDisplay + '/s'
            textWidth, textHeight = self.fonts[15].size(textDisplay)
            self.drawText(
                font=self.fonts[15], text=textDisplay, 
                color=self.colors['黑'], x=ui_x+150-textWidth/2, y=ui_y+100+25*i-textHeight, 
                surface=self.surface, alpha=255
            )
        # 显示元素
        self.drawButton(
            surface=self.surface, x=ui_x+75, y=ui_y+323, 
            width=150, height=30, 
            depth=0, text=self.data.language['element'], 
            shading=False, transparent=True
        )
        elements = (
            'element_qian', 'element_kun', 'element_zhen', 'element_xun', 
            'element_kan', 'element_li', 'element_gen', 'element_dui'
        )
        iconWidth, iconHeight = 32, 32
        j = 0
        for i, element in enumerate(elements):
            elementName = self.data.language[element]
            textWidth, textHeight = self.fonts[10].size(elementName)
            elementIcon = pg.transform.scale(self.data.elementImgs[element], (iconWidth, iconHeight))
            self.surface.blit(elementIcon, (ui_x+49+200*j-iconWidth/2, ui_y+350+(iconHeight+10)*(i//2)))
            self.drawText(
                font=self.fonts[10], text=elementName, 
                color=self.colors['黑'], x=ui_x+49+iconWidth+(100-iconWidth)*j*2-textWidth*j, y=ui_y+350+(iconHeight+10)*(i//2), 
                surface=self.surface, alpha=255
            )
            self.drawText(
                font=self.fonts[10], text=str(self.data.playerTotalValues[element]), 
                color=self.colors['黑'], x=ui_x+49+iconWidth+(100-iconWidth)*j*2-20*j, y=ui_y+350+(iconHeight+10)*(i//2)+textHeight+2, 
                surface=self.surface, alpha=255
            )
            j = 1 if j == 0 else 0
        # 陈列装备
        equipmentItems = []
        firstSquare = (14, 55)
        offsetX = 0
        offsetY = 52
        for i, itemAttr in enumerate(self.data.playerSave['equipment']):
            gridX, gridY = ui_x+firstSquare[0]+offsetX, ui_y+firstSquare[1]+offsetY*(i//2)
            # self.putdownHoldingItem(x=gridX, y=gridY, itemAttr=itemAttr, place='equipment', i=i)
            item = None
            if itemAttr != None:
                item = Item(data=self.data, surface=self.surface, camera=self.camera, attr=itemAttr)
                item.location = 'equipped'
                item.x, item.y = gridX, gridY
                item.update()
                item.rightClick(i=i)
            gridRect = pg.Rect(gridX, gridY, 33, 33)
            wearConditions = False
            if self.data.holdingItem != None:
                if self.data.holdingItem.attr['type'] == 0 and self.data.playerSave['level'] >= self.data.holdingItem.attr['required level']:
                    wearConditions = True
            conditions = (
                gridRect.collidepoint(pg.mouse.get_pos()), 
                pg.mouse.get_pressed()[0] == 1,
                self.data.holdingItem == None or wearConditions
            )
            if all(conditions):
                self.data.sounds['change equipment'].play()
                temp = self.data.holdingItem
                self.data.holdingItem = item
                item = temp
                self.data.playerSave['equipment'][i] = item.attr if item != None else None
                if self.data.playerSave['equipment'][i] != None:
                    self.data.playerChanged = True
                pg.time.wait(200)
            
            equipmentItems.append(item)
            offsetX = 234 if offsetX == 0 else 0
        for item in equipmentItems:
            if item != None:
                item.displayAttrHelper()

    def drawInGameOption(self):
        gotoID = self.id
        menuSize = (185, 300)
        buttonWidth, buttonHeight = 100, 62
        ui_x, ui_y = self.width-menuSize[0], self.height-menuSize[1]-buttonHeight-20
        pg.draw.rect(self.surface, self.colors['棕'], (ui_x, ui_y, *menuSize))
        # 保存按钮
        save = self.drawButton(
            surface=self.surface, x=ui_x+menuSize[0]/2-buttonWidth/2, y=ui_y+20, 
            width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['save']+'/'+self.data.language['load'], shading=True
        )
        # 返回菜单按钮
        goMenu = self.drawButton(
            surface=self.surface, x=ui_x+menuSize[0]/2-buttonWidth/2, y=ui_y+40+buttonHeight*2, 
            width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['back to menu'], shading=True
        )
        if save:
            self.showSaveLoadMenu = not self.showSaveLoadMenu
            self.userInput = ''
            # 打开save/load菜单,快捷键失效,为输入让位

            self.shortKey = not self.showSaveLoadMenu
        if self.showSaveLoadMenu:
            slMenuTopLeftX, slMenuTopLeftY = ui_x-menuSize[0]*2-1, ui_y-menuSize[1]
            pg.draw.rect(self.surface, self.colors['肉'], (slMenuTopLeftX, slMenuTopLeftY, menuSize[0]*2, menuSize[1]*2))
            self.displaySaveList(x=slMenuTopLeftX,y=slMenuTopLeftY,width=menuSize[0]*2,height=menuSize[1]*2)
            self.userInputFileName()
            self.drawText(
                font=self.fonts[20], text=self.data.language['save name']+': '+self.userInput[-20:]+self.insertPosMark, 
                color=self.colors['黑'], x=ui_x-menuSize[0]*2+10, y=ui_y+menuSize[1]-buttonHeight-50, 
                surface=self.surface, alpha=255
            )
            loadFile = self.drawButton(
                surface=self.surface, x=ui_x-menuSize[0]*2+menuSize[0]//5, y=ui_y+menuSize[1]-buttonHeight-10, 
                width=buttonWidth, height=buttonHeight, 
                depth=3, text=self.data.language['load'], shading=True
            )
            deleteFile = self.drawButton(
                surface=self.surface, x=ui_x-menuSize[0]-buttonWidth//3, y=ui_y+menuSize[1]-buttonHeight+10, 
                width=buttonWidth//1.5, height=buttonHeight//1.5, 
                depth=3, text=self.data.language['delete'], shading=True
            )
            saveFile = self.drawButton(
                surface=self.surface, x=ui_x-1-buttonWidth-menuSize[0]//5, y=ui_y+menuSize[1]-buttonHeight-10, 
                width=buttonWidth, height=buttonHeight, 
                depth=3, text=self.data.language['save'], shading=True
            )
            if loadFile:
                self.data.load(name=self.chosenSave)
                gotoID = -2
            if saveFile:
                if self.userInput != '':
                    self.data.save(name=self.userInput)
                    self.userInput = ''
                    self.saveList = self.data.loadSaveList()
            if deleteFile:
                savePath = os.path.join('save', self.chosenSave+'.cundang')
                if os.path.exists(savePath):
                    os.remove(savePath)
                    self.saveList = self.data.loadSaveList()
                    if self.saveList:
                        self.chosenSave = self.saveList[0]
        if goMenu:
            self.changeScene = True
            gotoID = 0
        return gotoID

    def drawUI(self):
        gotoID = self.id
        buttonWidth, buttonHeight = 100, 62
        # 返回菜单
        openMenu = self.drawButton(
            surface=self.surface, x=self.width-buttonWidth-50, y=self.height-buttonHeight-20, 
            width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['settings']+'('+pg.key.name(self.data.settings['key bindings']['settings']).upper()+')', 
            shading=True
        )
        if openMenu or self.eventInput['KEY_DOWN'] == self.data.settings['key bindings']['settings']:
            self.showInGameOption = not self.showInGameOption
            self.showSaveLoadMenu = False
            self.shortKey = not self.showSaveLoadMenu
        # 显示姓名
        self.drawText(
            font=self.fonts[20], text=self.data.playerSave['name'], 
            color=self.colors['黑'], x=20, y=20, 
            surface=self.surface, alpha=255
        )
        # 显示头像
        playerProfileImg = self.data.images['touxiang'+str(self.data.playerSave['profile image'])].convert_alpha()
        playerProfileImg = pg.transform.scale(playerProfileImg, (64, 64))
        self.surface.blit(playerProfileImg, (20, 50))
        # 显示等级
        self.drawText(
            font=self.fonts[20], text=self.data.language['level']+': '+str(self.data.playerSave['level']), 
            color=self.colors['黑'], x=20, y=120, 
            surface=self.surface, alpha=255
        )
        # 数值条参数
        paramRectLength = 300
        # 显示生命值
        pg.draw.rect(surface=self.surface, color=self.colors['红粉'], rect=(150, 20, paramRectLength*(self.data.playerSave['current hp']/self.data.playerTotalValues['max hp']), 30))
        self.drawText(
            font=self.fonts[20], text=self.data.language['hp']+': '+str(self.data.playerSave['current hp'])+'/'+str(self.data.playerTotalValues['max hp']), 
            color=self.colors['黑'], x=150, y=20, 
            surface=self.surface, alpha=255
        )
        self.drawFrame(
            surface=self.surface, x=150, y=20, 
            width=paramRectLength, height=30, 
            color=self.colors['黄绿2'], lineSize=3
        )
        # 显示经验值
        pg.draw.rect(surface=self.surface, color=self.colors['金'], rect=(150, 55, paramRectLength*(self.data.playerSave['current exp']/self.data.playerSave['levelup exp']), 30))
        self.drawText(
            font=self.fonts[20], text=self.data.language['exp']+': '+str(int(self.data.playerSave['current exp']))+'/'+str(self.data.playerSave['levelup exp']), 
            color=self.colors['黑'], x=150, y=55, 
            surface=self.surface, alpha=255
        )
        self.drawFrame(
            surface=self.surface, x=150, y=55, 
            width=paramRectLength, height=30, 
            color=self.colors['黄绿2'], lineSize=3
        )
        # 显示背包按钮
        backPack = self.drawButton(
            surface=self.surface, x=500, y=20, 
            width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['backpack']+'('+pg.key.name(self.data.settings['key bindings']['backpack']).upper()+')',
            shading=True
        )
        if backPack or (self.eventInput['KEY_DOWN'] == self.data.settings['key bindings']['backpack'] and self.shortKey):
            self.showBackpack = not self.showBackpack
            self.backpackPage = 0
        # 显示人物按钮
        playerAttr = self.drawButton(
            surface=self.surface, x=550+buttonWidth, y=20, 
            width=buttonWidth, height=buttonHeight, 
            depth=3, text=self.data.language['player attributes']+'('+pg.key.name(self.data.settings['key bindings']['player attributes']).upper()+')', 
            shading=True
        )
        if playerAttr or (self.eventInput['KEY_DOWN'] == self.data.settings['key bindings']['player attributes'] and self.shortKey):
            self.showPlayerAttr = not self.showPlayerAttr
            # print(f'backpack is ', self.data.playerSave['backpack'])
        # 打开游戏内菜单
        if self.showInGameOption:
            gotoID = self.drawInGameOption()
        if self.showBackpack:
            self.drawInventory()
        if self.showPlayerAttr:
            self.drawPlayerAttr()
        self.drawHoldingItem()
        return gotoID

    def update(self):
        super().update()
        # if pg.mouse.get_pressed()[1] == 1:
        #     pass
        return self.drawUI()