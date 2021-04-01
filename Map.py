 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, random
from Player import Player
from Item import Item
from Merchant import Merchant

class Map(GameBase):
    def __init__(self, data, surface, camera):
        super().__init__(data, surface)
        self.id = 6
        self.camera = camera
        # self.InBuildingScreen = InBuildingScreen(data=self.data, surface=self.surface)
        self.field = (self.drawCity, self.drawBattleField)
        self.fieldIndex = 0
        self.debugButton = True
        self.itemsOnGround = []
        self.buildingXY, self.buildingImgs = [], []
        self.battleType = -1
        self.mapColors = {
            'home': (self.colors['雪白'], self.colors['肉'], self.colors['肉粉']), 
            0: (self.colors['靛蓝'], self.colors['白棕2'], self.colors['黄3']), 
            1: (self.colors['绿白'], self.colors['棕白'], self.colors['粉棕']), 
            2: (self.colors['金'], self.colors['金2'], self.colors['桔'])
        }
        self.color = random.choice(self.mapColors['home'])
        self.mapMarginBg = self.data.images['tree_margin'].convert_alpha()
        self.genRandomBuildings()
        # delete me
        self.img = random.choice(tuple(self.data.images.values()))
        self.merchantHeadImg, self.merchantBodyImg = None, None
        self.merchant = Merchant(data=self.data, surface=self.surface, camera=self.camera)
        self.switchedMap = False
        self.showmainbaseMenu = False
        self.canSwitchMap = True
        self.replaceMerchant = True
    
    def updateVars(self):
        super().updateVars()
        self.fieldIndex = 0
        self.battleType = -1
        self.showmainbaseMenu = False
        self.replaceMerchant = True
    
    def genRandomBuildings(self):
        buildingNum = random.randint(10, 20)
        self.buildingXY, self.buildingImgs = [], []
        for _ in range(buildingNum):
            buildingIndex = random.randint(0, 113)
            buildingImg = self.data.buildingImgs['building '+str(buildingIndex)]
            buildingX = random.randint(2, 24)*200
            buildingY = random.randint(2, 24)*200
            while (buildingX, buildingY) in self.buildingXY and len(self.buildingImgs)<buildingNum:
                buildingX = random.randint(2, 20)*200
                buildingY = random.randint(2, 20)*200
            self.buildingXY.append((buildingX, buildingY))
            self.buildingImgs.append(buildingImg)

    def randomMerchant(self):
        merchantHead = random.randint(1, 21)
        merchantBody = random.randint(0, 5)
        headImg = pg.transform.scale(self.data.images['merchant head '+str(merchantHead)].convert_alpha(), (90, 90))
        bodyImg = pg.transform.scale(self.data.images['merchant body '+str(merchantBody)].convert_alpha(), (90, 150))
        return headImg, bodyImg

    def randomMonsters(self):
        monsterNumRanges = ((1, 2),(10, 20))
        monsterTypeList = ('boss', 'monster')
        monsterTypeIndex = ((0, 1), (0, 9))
        if self.battleType in (0, 1):
            monsterNum = random.randint(monsterNumRanges[self.battleType][0], monsterNumRanges[self.battleType][1])
            monsterType = monsterTypeList[self.battleType]
            monsterIndex = random.randint(monsterTypeIndex[self.battleType][0], monsterTypeIndex[self.battleType][1])
            return monsterNum, monsterType+str(monsterIndex)
        else:
            return None, None

    def randomXY(self, range):
        return random.randint(range[0], range[1]), random.randint(range[0], range[1])

    def switchMap(self, index):
        self.fieldIndex = index
        self.switchedMap = True
        if self.fieldIndex == 0:
            self.color = random.choice(self.mapColors['home'])
            self.genRandomBuildings()
        elif self.fieldIndex == 1:
            mapType = random.random()
            if mapType < 0.1:
                self.battleType = 2 # 0 老怪, 1 小怪, 2 商人
                self.merchantHeadImg, self.merchantBodyImg = self.randomMerchant()
            elif mapType >= 0.1 and mapType < 0.2:
                self.battleType = 0
            else:
                self.battleType = 1
            self.color = random.choice(self.mapColors[self.battleType])

    def drawCity(self):
        self.replaceMerchant = True
        self.surface.fill(self.color)
        x, y = self.camera.stickToCamera(0, 0)
        self.surface.blit(self.mapMarginBg, (x, y))
        #提示
        tipTextX, tipTextY = self.camera.stickToCamera(self.width-250, -50)
        self.drawButton(
            surface=self.surface, x=tipTextX, y=tipTextY, 
            width=200, height=45, 
            depth=0, text=self.data.language['click to enter'], 
            shading=False, transparent=True
        )
        # 渲染主基地
        mainbaseWidth, mainbaseHeight = self.data.buildingImgs['building main base'].get_size()
        mainbaseX, mainbaseY = self.camera.stickToCamera(self.width/2, 200)
        mainbaseHereText = self.data.language['main base'] + '-->'
        textWidth, textHeight = self.fonts[20].size(mainbaseHereText)
        mainbaseHereTextX, mainbaseHereTextY = mainbaseX-textWidth-10, mainbaseY+mainbaseHeight/2-textHeight/2
        self.drawText(
            font=self.fonts[20], text=mainbaseHereText, 
            color=self.colors['黑'], x=mainbaseHereTextX, y=mainbaseHereTextY, 
            surface=self.surface, alpha=255
        )
        mainBase = self.drawButton(
                surface=self.surface, x=mainbaseX, y=mainbaseY, 
                width=mainbaseWidth, height=mainbaseHeight, depth=0, 
                image=self.data.buildingImgs['building main base'], shading=False
            )
        if mainBase:
            self.showmainbaseMenu = True
        # 渲染其他房子
        for xy, img in zip(self.buildingXY, self.buildingImgs):
            imgWidth, imgHeight = img.get_size()
            x, y = self.camera.stickToCamera(xy[0], xy[1])
            isClicked = self.drawButton(
                    surface=self.surface, x=x, y=y, 
                    width=imgWidth, height=imgHeight, depth=0, 
                    image=img, shading=False
                )
            if isClicked and self.canSwitchMap:
                self.switchMap(1)
        return self.mapMarginBg.get_width()-200, self.mapMarginBg.get_width()-300 # limitX, limitY

    def drawBattleField(self):
        self.surface.fill(self.color)
        x, y = self.camera.stickToCamera(0, 0)
        self.surface.blit(self.mapMarginBg, (x, y))
        # mapName = ('老怪', '小怪', '商人')
        # self.drawText(
        #     font=self.fonts[15], text=mapName[self.battleType], 
        #     color=self.colors['黑'], x=self.width/2, y=10, 
        #     surface=self.surface, alpha=255
        # )
        exitImg = pg.transform.scale(self.data.images['door exit'].convert_alpha(), (32, 32))
        exitImgWidth, exitImgHeight = exitImg.get_size()
        goHomeText = self.data.language['click to go home']+'-->'
        textWidth, textHeight = self.fonts[15].size(goHomeText)
        textX, textY = self.width-exitImgWidth-textWidth-50, 20+textHeight/2
        exitX, exitY = self.width-exitImgWidth-10, 20
        self.drawText(
            font=self.fonts[15], text=goHomeText, 
            color=self.colors['黑'], x=textX, y=textY, 
            surface=self.surface, alpha=255
        )
        exit = self.drawButton(
                surface=self.surface, x=exitX, y=exitY, 
                width=exitImgWidth, height=exitImgHeight, depth=0, 
                image=exitImg, shading=False
        )
        if exit:
            self.switchMap(0)
            self.battleType = -1
        return self.mapMarginBg.get_width()-200, self.mapMarginBg.get_width()-300 # limitX, limitY

    def drawMerchant(self):
        if self.replaceMerchant:
            self.merchant = Merchant(data=self.data, surface=self.surface, camera=self.camera)
            self.replaceMerchant = False
        x, y = self.camera.stickToCamera(self.width/2+1000, self.height/2)
        textWidth, textHeight = self.fonts[30].size(self.data.language['bullion merchant'])
        self.drawText(
            font=self.fonts[30], text=self.data.language['bullion merchant'], 
            color=self.colors['黑'], x=x+self.merchantHeadImg.get_width()/2-textWidth/2, y=y-70-textHeight, 
            surface=self.surface, alpha=255
        )
        self.surface.blit(self.merchantBodyImg, (x, y))
        self.surface.blit(self.merchantHeadImg, (x, y-60))
        merchantButton = self.drawButton(
            surface=self.surface, x=x, y=y, 
            width=90, height=210, 
            depth=0, text=None, 
            shading=False, transparent=True
        )
        if merchantButton:
            self.merchant.showMenu = True

    def update(self):
        super().update()
        limitX, limitY = self.field[self.fieldIndex]()
        if self.battleType == 2:
            self.merchant.eventInput = self.eventInput
            self.drawMerchant()
            self.merchant.update()
        return limitX, limitY
