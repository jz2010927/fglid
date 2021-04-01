 # -*- coding: utf-8 -*-
from GameBase import GameBase
import pygame as pg, os, math

class Menu(GameBase):
    def __init__(self, data, surface):
        super().__init__(data, surface)
        self.id = 0
        self.buttonWidth, self.buttonHeight = 150, 93
        self.buttonNames = (
            self.data.language['new game'], self.data.language['load game'], self.data.language['option'], 
            self.data.language['tutorial'], self.data.language['credits'], self.data.language['quit']
        )
        self.showMenu = False
        self.titleFontSize = 0
        self.bgmLoaded = False
    
    def updateVars(self):
        super().updateVars()
        self.bgmLoaded = False
        self.buttonNames = (
            self.data.language['new game'], self.data.language['load game'], self.data.language['option'], 
            self.data.language['tutorial'], self.data.language['credits'], self.data.language['quit']
        )
        
    def startScreen(self):
        self.surface.fill(self.colors['白'])
        finalTextWidth, finalTextHeight = 200, 124
        textWidth, textHeight = self.fonts[self.titleFontSize].size(self.data.language['game title'])
        self.drawText(
            font=self.fonts[self.titleFontSize], 
            text=self.data.language['game title'], 
            color=self.colors['黑'], 
            x=self.width/2-textWidth/2, y=self.height/2-textHeight/2, 
            surface=self.surface, alpha=255
        )
        if textWidth < finalTextWidth or textHeight < finalTextHeight:
            if self.titleFontSize < 71:
                self.titleFontSize += 1
        if not self.bgmLoaded:
            pg.mixer.music.unload()
            pg.mixer.music.load(os.path.join('assets', 'sounds', 'start_screen_bgm.ogg'))
            pg.mixer.music.set_volume(self.data.settings['sound volume'][0] * self.data.settings['sound volume'][1])
            pg.mixer.music.play(0)
            self.bgmLoaded = True

    def chooseLanguage(self):
        # defines
        width = 210
        arrowImageSize = (32, 32)
        # draw language choose title
        textWidth, textHeight = self.fonts[20].size(self.data.language['language'])
        self.drawText(
            font=self.fonts[20], text=self.data.language['language'], 
            color=self.colors['黑'], x=self.width/2-textWidth/2, y=self.height/4-arrowImageSize[1]*2, 
            surface=self.surface, alpha=255
        )
        # load images
        leftArrowImg = self.data.images['left arrow'].convert_alpha()
        leftArrowImg = pg.transform.scale(leftArrowImg, arrowImageSize)
        clickedLeftArrowImg = self.data.images['left arrow clicked'].convert_alpha()
        clickedLeftArrowImg = pg.transform.scale(clickedLeftArrowImg, arrowImageSize)
        # load language list
        languageList = list(self.data.languageList.values())
        # draw arrows
        languageIndex = self.arrowSelect(
            surface=self.surface, x=self.width/2-width/2, y=self.height/4, width=width, 
            leftArrowImg=leftArrowImg, clickedLeftArrowImg=clickedLeftArrowImg, 
            currentIndex=languageList.index(self.data.settings['language']), listLength=len(languageList)
        )
        # draw language text
        textWidth, textHeight = self.fonts[20].size(list(self.data.languageList.keys())[languageIndex])
        self.drawText(
            font=self.fonts[20], text=list(self.data.languageList.keys())[languageIndex], 
            color=self.colors['黑'], x=self.width/2+textWidth/2+arrowImageSize[0]-width/2, y=self.height/4, 
            surface=self.surface, alpha=255
        )
        # set language settings
        self.data.settings['language'] = languageList[languageIndex]
        self.data.language = self.data.loadLanguage()
        # draw click to start button
        self.showMenu = self.drawButton(
            surface=self.surface, x=self.width/2-self.buttonWidth, y=self.height*0.9-self.buttonHeight, 
            width=self.buttonWidth*2, height=self.buttonHeight, depth=3, text=self.data.language['click to start']
        )
        if self.showMenu:
            self.buttonNames = (
                self.data.language['new game'], self.data.language['load game'], self.data.language['option'], 
                self.data.language['tutorial'], self.data.language['credits'], self.data.language['quit']
            )
            self.data.saveSettings()

    def mainMenu(self):
        self.data.sounds['start screen bgm'].stop()
        gotoID = self.id
        self.surface.fill(self.colors['棕'])
        margin_x, margin_y = 20, 50
        for i, name in enumerate(self.buttonNames):
            selected = self.drawButton(surface=self.surface, x=margin_x, y=margin_y+self.height*i/(len(self.buttonNames)+1), width=self.buttonWidth, height=self.buttonHeight, depth=3, text=name)
            if selected:
                if i == len(self.buttonNames)-1:
                    gotoID = -1
                else:
                    gotoID = i + 1
                self.changeScene = True
        return gotoID

    def update(self):
        super().update()
        gotoID = self.id
        self.updateVars()
        if self.showMenu:
            gotoID = self.mainMenu()
            self.changeScene = True
        else:
            self.startScreen()
            self.chooseLanguage()
        return gotoID

if __name__ == '__main__':
    import sys
    from Data import Data
    data = Data()
    pg.init()
    if data.settings['full screen']:
        screen = pg.display.set_mode(data.settings['resolution'], pg.RESIZABLE|pg.FULLSCREEN, 32)
    else:
        screen = pg.display.set_mode(data.settings['resolution'], pg.RESIZABLE, 32)
    clock = pg.time.Clock()
    app = Menu(data=data, surface=screen)
    run = True
    while run:
        clock.tick(data.settings['fps'])
        app.resetEventInputs()
        # app.eventInput = dict.fromkeys(app.eventInput.iterkeys(), None)
        # app.eventInput['MOUSE_BUTTON_UP'], app.eventInput['MOUSE_POS'] = None, None
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONUP:
                if event.button <= 5:
                    app.eventInput['MOUSE_BUTTON_UP'] = event.button
                    app.eventInput['MOUSE_POS'] = pg.mouse.get_pos()
                else:
                    print('unknown mouse button')
            if event.type == pg.VIDEORESIZE:
                if data.settings['full screen']:
                    screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE|pg.FULLSCREEN)
                else:
                    screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
        app.update()
        pg.display.update()
    pg.quit()
    sys.exit()