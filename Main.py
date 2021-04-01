 # -*- coding: utf-8 -*-
import pygame as pg, sys, os
from Data import Data
from Menu import Menu
from Credits import Credits
from BattleField import BattleField
from Option import Option
from NewGame import NewGame
from Tutorial import Tutorial
from LoadGame import LoadGame
from Camera import Camera

class Main():
    def __init__(self):
        pg.init()
        self.data = Data()
        # pg.USEREVENT +0 ~ +8
        pg.time.set_timer(pg.USEREVENT+8, 100) # 0.1s
        self.initVars()

    def initVars(self):
        self.running, self.playing = False, False
        self.screen = pg.display.set_mode(self.data.settings['resolution'], pg.RESIZABLE, 32)
        if self.data.settings['full screen']:
            self.screen = pg.display.set_mode(self.data.settings['resolution'], pg.RESIZABLE|pg.FULLSCREEN, 32)
        self.data.loadAssetsToRam()
        self.caption = self.data.language['game title']
        self.icon = self.data.images['icon'].convert_alpha()
        pg.display.set_caption(self.caption)
        pg.display.set_icon(self.icon)
        self.camera = Camera(data=self.data, surface=self.screen)
        self.sceneIDs = {
            0: Menu(data=self.data, surface=self.screen), 
            1: NewGame(data=self.data, surface=self.screen), # new game
            2: LoadGame(data=self.data, surface=self.screen), # load game
            3: Option(data=self.data, surface=self.screen), # option
            4: Tutorial(data=self.data, surface=self.screen), # tutorial
            5: Credits(data=self.data, surface=self.screen), # credits
            6: BattleField(data=self.data, surface=self.screen, camera=self.camera), # gaming
            -1: self.exit # quit
        }
        self.currentSceneID = 0
        self.clock = pg.time.Clock()

    def start(self):
        self.running = True
        while self.running:
            app = self.sceneIDs[self.currentSceneID]
            self.playing = self.currentSceneID == 6
            if self.currentSceneID >= 0:
                app.resetEventInputs()
            else:
                app()
            self.clock.tick(self.data.settings['fps'])
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running, self.playing = False, False
                elif event.type == pg.KEYDOWN:
                   app.eventInput['KEY_DOWN'] = event.key
                   app.eventInput['KEY_UNICODE'] = event.unicode
                elif event.type == pg.KEYUP:
                    app.eventInput['KEY_UP'] = event.key
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button <= 7:
                        app.eventInput['MOUSE_BUTTON_DOWN'] = event.button
                        app.eventInput['MOUSE_POS'] = pg.mouse.get_pos()
                    else:
                        print('unknown mouse button')
                elif event.type == pg.MOUSEBUTTONUP:
                    if event.button <= 7:
                        app.eventInput['MOUSE_BUTTON_UP'] = event.button
                        app.eventInput['MOUSE_POS'] = pg.mouse.get_pos()
                    else:
                        print('unknown mouse button')
                elif event.type in [pg.USEREVENT+i for i in range(9)]:
                    if self.currentSceneID == 6:
                        if event.type == pg.USEREVENT: # player update anim
                            app.updatePlayerAnim()
                        elif event.type == pg.USEREVENT + 1: # monster attack speed
                            app.updateMonsterAnim()
                        elif event.type == pg.USEREVENT + 2: # player hp recovery
                            app.playerHpRecovery()
                        elif event.type == pg.USEREVENT + 3:
                            app.playerShoot()
                    if event.type == pg.USEREVENT + 8:
                        if app.timer > 0:
                            app.countDown()
            if self.currentSceneID >= 0:
                self.currentSceneID = app.update()
            pg.display.update()
        pg.quit()
        sys.exit()

    def exit(self):
        self.running, self.playing = False, False
        pg.quit()
        sys.exit()

if __name__ == '__main__':
    app = Main()
    app.start()