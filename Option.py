 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, copy

class Option(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.id = 3
        self.tempSettings = copy.deepcopy(self.data.settings)
        self.leftArrowImg = (
            self.data.images['left arrow'].convert_alpha(), 
            self.data.images['left arrow clicked'].convert_alpha()
        )
        self.topics = (
            self.drawGraphicOption, 
            self.drawSoundOption, 
            self.drawGameOption, 
            self.drawControlsOption
        )
        self.topicSelected = 0
        self.keyListening = None
        self.cameraSpeedList = [i for i in range(10, 310, 10)]
    
    def updateVars(self):
        super().updateVars()
        self.tempSettings = copy.deepcopy(self.data.settings)

    def drawTopic(self):
        buttonWidth, buttonHeight = 100, 62
        marginY = 20
        topicTitle = (self.data.language['graphics'], self.data.language['sound'], self.data.language['game'], self.data.language['controls'])
        for i, title in enumerate(topicTitle):
            x, y = self.width/len(topicTitle)*(i+0.5)-buttonWidth/2, marginY
            isClicked = self.drawButton(
                surface=self.surface, x=x, y=y, width=buttonWidth, height=buttonHeight, 
                depth=0, text=title, shading=False
            )
            if isClicked:
                self.topicSelected = i
        pg.draw.line(
            surface=self.surface, color=self.colors['黑'], 
            start_pos=(self.width/len(topicTitle)*(self.topicSelected+0.5)-buttonWidth/2, marginY+buttonHeight), 
            end_pos=(self.width/len(topicTitle)*(self.topicSelected+0.5)+buttonWidth/2, marginY+buttonHeight), width=2
        )

    def drawBottomButtons(self):
        buttonWidth, buttonHeight = 150, 90
        marginY = 20
        gotoID = self.id
        buttonNames = (self.data.language['back'], self.data.language['set default'], self.data.language['save'])
        for i, name in enumerate(buttonNames):
            x, y = self.width/len(buttonNames)*(i+0.5)-buttonWidth/2, self.height-buttonHeight-marginY
            isClicked = self.drawButton(
                surface=self.surface, x=x, y=y, width=buttonWidth, height=buttonHeight, 
                depth=3, text=name, shading=True
            )
            if isClicked:
                if i == 0:
                    self.tempSettings = copy.deepcopy(self.data.settings)
                    gotoID = 0
                elif i == 1:
                    self.tempSettings = copy.deepcopy(self.data.defaultSettings)
                elif i == 2:
                    self.data.settings = copy.deepcopy(self.tempSettings)
                    self.data.saveSettings()
                    self.data.language = self.data.loadLanguage()
                    pg.mixer.music.set_volume(self.data.settings['sound volume'][0] * self.data.settings['sound volume'][1])
                    for k,v in self.data.sounds.items():
                        if 'bgm' in k:
                            v.set_volume(self.data.settings['sound volume'][0] * self.data.settings['sound volume'][1])
                        else:
                            v.set_volume(self.data.settings['sound volume'][0] * self.data.settings['sound volume'][2])
                    gotoID = 0
        textWidth, textHeight = self.fonts[20].size(self.data.language['may need restart'])
        self.drawText(
            font=self.fonts[20], text=self.data.language['may need restart'], 
            color=self.colors['黑'], x=self.width/2-textWidth/2, y=self.height-textHeight-buttonHeight-marginY*2, 
            surface=self.surface, alpha=100
        )
        return gotoID

    def drawGraphicOption(self):
        # 分辨率
        width = 210
        arrowSize = (32, 32)
        leftArrow, leftArrowClicked = pg.transform.scale(self.leftArrowImg[0], arrowSize), pg.transform.scale(self.leftArrowImg[1], arrowSize)
        text = str(self.tempSettings['resolution'][0]) + ' x ' + str(self.tempSettings['resolution'][1])
        textWidth, textHeight = self.fonts[20].size(text)
        self.drawText(
            font=self.fonts[20], text=self.data.language['resolution'], 
            color=self.colors['黑'], x=self.width/2-width/2-arrowSize[0]-100, y=self.height/5-textHeight/2+arrowSize[1]/2, 
            surface=self.surface, alpha=255
        )
        self.drawText(
            font=self.fonts[20], text=text, 
            color=self.colors['黑'], x=self.width/2-textWidth/2+arrowSize[0]/2, y=self.height/5-textHeight/2+arrowSize[1]/2, 
            surface=self.surface, alpha=255
        )
        index = 0
        try:
            index = self.arrowSelect(
                surface=self.surface, x=self.width/2-width/2, y=self.height/5, width=width, 
                leftArrowImg=leftArrow, clickedLeftArrowImg=leftArrowClicked, 
                currentIndex=self.resolution.index(tuple(self.tempSettings['resolution'])), listLength=len(self.resolution)
            )
        except:
            pass
        self.tempSettings['resolution'] = self.resolution[index]

        # 全屏
        textWidth, textHeight = self.fonts[20].size(self.data.language['full screen'])
        fullScreenClicked = self.drawButton(
            surface=self.surface, x=self.width/2-width/2-arrowSize[0]+textWidth, y=self.height/1.8+arrowSize[1]/2-textHeight, 
            width=25, height=25, colors=(self.colors['白'], self.colors['白棕'], self.colors['粉棕']), 
            depth=3, shading=False
        )
        self.drawText(
            font=self.fonts[20], text=self.data.language['full screen'], 
            color=self.colors['黑'], x=self.width/2-width/2-arrowSize[0]-100, y=self.height/1.8-textHeight+arrowSize[1]/2, 
            surface=self.surface, alpha=255
        )
        if fullScreenClicked:
            self.tempSettings['full screen'] = not self.tempSettings['full screen']
        if self.tempSettings['full screen']:
            self.drawCorrectMark(surface=self.surface, area=(self.width/2-width/2-arrowSize[0]+textWidth, self.height/1.8+arrowSize[1]/2-textHeight, 25, 25), color=self.colors['黑'], lineSize=3)

    def drawSoundOption(self):
        slideAreaWidth, slideAreaHeight = 300, 100
        textX = self.width/4
        textY = self.height/4
        offsetX, offsetY = 100, 120
        volumeAreaName = (self.data.language['total volume'], self.data.language['music volume'], self.data.language['sfx volume'])
        for i, name in enumerate(volumeAreaName):
            self.drawText(
                surface=self.surface, font=self.fonts[19], text=name, 
                color=self.colors['黑'], x=textX, y=textY+offsetY*i, alpha=255
            )
            v = self.drawSlideArea(
                surface=self.surface, x=textX+250+offsetX, y=textY+offsetY*i-slideAreaHeight/2, 
                width=slideAreaWidth, height=slideAreaHeight, 
                volume=self.tempSettings['sound volume'][i]
            )
            self.drawText(
                surface=self.surface, font=self.fonts[19], text=str(int(v*100))+'%', 
                color=self.colors['黑'], x=textX+235, y=textY+offsetY*i, alpha=255
            )
            self.tempSettings['sound volume'][i] = v

    def drawGameOption(self):
        # 语言选择
        width = 210
        arrowSize = (32, 32)
        leftArrow, leftArrowClicked = pg.transform.scale(self.leftArrowImg[0], arrowSize), pg.transform.scale(self.leftArrowImg[1], arrowSize)
        languageList, languageNameList = list(self.data.languageList.values()), list(self.data.languageList.keys())
        languageIcon = pg.image.load(os.path.join('languages', self.tempSettings['language']+'.png')).convert_alpha()
        languageIcon = pg.transform.scale(languageIcon, (45, 30))
        index_language = self.arrowSelect(
            surface=self.surface, x=self.width/2-width/2, y=self.height/5, width=width, 
            leftArrowImg=leftArrow, clickedLeftArrowImg=leftArrowClicked, 
            currentIndex=languageList.index(self.tempSettings['language']), listLength=len(self.data.languageList)
        )
        self.tempSettings['language'] = languageList[index_language]
        textWidth, textHeight = self.fonts[20].size(languageNameList[index_language])
        self.drawText(
            surface=self.surface, font=self.fonts[19], text=languageNameList[index_language], 
            color=self.colors['黑'], x=self.width/2+arrowSize[0]/2-textWidth/2, y=self.height/5, alpha=255
        )
        self.drawText(
            font=self.fonts[20], text=self.data.language['language'], 
            color=self.colors['黑'], x=self.width/2-textWidth-200, y=self.height/5, 
            surface=self.surface, alpha=255
        )
        self.surface.blit(languageIcon, (self.width/2+width, self.height/5))
        # # 镜头移动速度选择
        # self.drawText(
        #     font=self.fonts[20], text=self.data.language['camera speed'], 
        #     color=self.colors['黑'], x=self.width/4, y=self.height/3, 
        #     surface=self.surface, alpha=255
        # )
        # self.drawText(
        #     font=self.fonts[20], text=str(self.tempSettings['camera speed']), 
        #     color=self.colors['黑'], x=self.width/4+200+width/2, y=self.height/3, 
        #     surface=self.surface, alpha=255
        # )
        # index_cameraSpeed = self.arrowSelect(
        #     surface=self.surface, x=self.width/4+200, y=self.height/3, width=width, 
        #     leftArrowImg=leftArrow, clickedLeftArrowImg=leftArrowClicked, 
        #     currentIndex=self.cameraSpeedList.index(self.tempSettings['camera speed']), listLength=len(self.cameraSpeedList)
        # )
        # self.tempSettings['camera speed'] = self.cameraSpeedList[index_cameraSpeed]
        # 刷新率选择
        self.drawText(
            font=self.fonts[20], text=self.data.language['fps'], 
            color=self.colors['黑'], x=self.width/2-textWidth/2-200, y=self.height/1.5, 
            surface=self.surface, alpha=255
        )
        index_fps = self.arrowSelect(
            surface=self.surface, x=self.width/2-width/2, y=self.height/1.5, width=width, 
            leftArrowImg=leftArrow, clickedLeftArrowImg=leftArrowClicked, 
            currentIndex=self.fpsList.index(self.tempSettings['fps']), listLength=len(self.fpsList)
        )
        self.tempSettings['fps'] = self.fpsList[index_fps]
        self.drawText(
            font=self.fonts[20], text=str(self.fpsList[index_fps]), 
            color=self.colors['黑'], x=self.width/2, y=self.height/1.5, 
            surface=self.surface, alpha=255
        )

    def drawControlsOption(self):
        keys = ('up', 'down', 'left', 'right', 'backpack', 'player attributes', 'settings')
        buttonWidth, buttonHeight = 150, 90
        for i, k in enumerate(keys):
            j = i-4 if i > 3 else i
            buttonX, buttonY = self.width/10+(buttonWidth+20)*j, (self.height/20+buttonHeight)*((i//4)+1), 
            keyName = self.data.language[k]
            isClicked = self.drawButton(
                    surface=self.surface, x=buttonX, y=buttonY, width=buttonWidth, height=buttonHeight, 
                    depth=0, text=keyName+': '+pg.key.name(self.tempSettings['key bindings'][k]).upper(), shading=False
                )  
            if isClicked:
                self.keyListening = k
        if self.keyListening != None:
            self.drawText(
                font=self.fonts[20], text=self.data.language['listening']+': '+self.data.language[self.keyListening], 
                color=self.colors['黑'], x=self.width/2-60, y=self.height/2-50, 
                surface=self.surface, alpha=255
            )
            if self.eventInput['KEY_DOWN'] != None:
                self.tempSettings['key bindings'][self.keyListening] = self.eventInput['KEY_DOWN']
                self.keyListening = None


    def update(self):
        super().update()
        self.surface.fill(self.colors['棕'])
        gotoID = self.id
        self.drawTopic()
        self.topics[self.topicSelected]()
        gotoID = self.drawBottomButtons()
        if gotoID != self.id:
            self.changeScene = True
        return gotoID