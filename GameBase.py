 # -*- coding: utf-8 -*-
import pygame as pg, os, json, random, math
from Data import Data

class GameBase:
    def __init__(self, data, surface):
        pg.init()
        self.eventInput = {
            'KEY_DOWN': None, 
            'KEY_UP': None, 
            'KEY_UNICODE': None, 
            'MOUSE_BUTTON_DOWN': None, 
            'MOUSE_BUTTON_UP': None, 
            'MOUSE_POS': None
        }
        self.data = data
        self.surface = surface
        self.fonts = self.data.fonts
        self.fonts2 = self.data.fonts2
        self.saveList = self.data.loadSaveList()
        self.chosenSave, self.saveListPage = '', 0
        if self.saveList:
            self.chosenSave = self.saveList[0]
        self.width, self.height = self.currentSize()
        self.colors = self.data.colors
        self.resolution = self.data.resolutionList
        self.fpsList = self.data.fpsList
        self.changeScene = True
        self.timer = 0

    def updateVars(self):
        pass
    
    def countDown(self):
        self.timer -= 0.1
        if self.timer <= 0:
            timeOut = True
        print(self.timer)

    def resetEventInputs(self):
        self.eventInput = {
            'KEY_DOWN': None, 
            'KEY_UP': None, 
            'KEY_UNICODE': None, 
            'MOUSE_BUTTON_DOWN': None, 
            'MOUSE_BUTTON_UP': None, 
            'MOUSE_POS': None
        }

    def setEventTimer(self, event=pg.USEREVENT, timer=200):
        pg.time.set_timer(event, timer)
        
    def isHappening(self, chance):
        hit = False
        if chance <= 0.0:
            hit = False
        elif chance >= 1.0:
            hit = True
        else:
            hit = True if random.random() <= chance else False
        return hit

    def playSound(self, sound, volume): # 1: music, 2: sound effect
        sound.set_volume(volume)
        sound.play()

    def currentSize(self):
        return pg.display.Info().current_w, pg.display.Info().current_h
        
    def isClicked(self, Rect, click=0, pos=None): # click: 0 左键, 1 中键, 2 右键
        if self.eventInput['MOUSE_BUTTON_UP'] == click+1: # 单击
            if Rect.collidepoint(self.eventInput['MOUSE_POS']): 
                return 3
        if Rect.collidepoint(pg.mouse.get_pos()): # 按下
            if pg.mouse.get_pressed()[click] == 1:
                return 1 # 按下
            else:
                return 2 # 悬浮
        return 0 # 未触碰
    
    def replaceImageColor(self, image, originalColor, targetColor):
        temp = pg.PixelArray(image)
        temp.replace(originalColor, targetColor)
        del temp
    
    def drawCorrectMark(self, surface, area, color, lineSize=2):
        middleX, middleY = area[0]+area[2]/2, area[1]+area[3]/2
        pg.draw.line(surface, color, (area[0], middleY), (middleX, area[1]+area[3]), lineSize)
        pg.draw.line(surface, color, (middleX, area[1]+area[3]), (area[0]+area[2], area[1]), lineSize)

    def drawText(self, font, text, color, x, y, surface, alpha=255):
        textSurface = font.render(text, True, color)
        textSurface.set_alpha(alpha)
        textRect = textSurface.get_rect()
        textRect.x, textRect.y = x, y
        surface.blit(textSurface, textRect)
        return textRect

    def drawFrame(self, surface, x, y, width, height, color, lineSize):
        # top
        pg.draw.line(surface, color, (x, y), (x+width, y), lineSize)
        # left
        pg.draw.line(surface, color, (x, y), (x, y+height), lineSize)
        # bottom
        pg.draw.line(surface, color, (x, y+height), (x+width, y+height), lineSize)
        # right
        pg.draw.line(surface, color, (x+width, y), (x+width, y+height), lineSize)

    def drawShading(self, surface, coordinates, lineSize, pressed=False):
        topLeft, bottomRight = '白', '黑'
        if pressed:
            topLeft, bottomRight = '黑', '白'
        # top
        pg.draw.line(surface, self.colors[topLeft], (coordinates[0], coordinates[1]), (coordinates[0]+coordinates[2], coordinates[1]), lineSize)
        # left
        pg.draw.line(surface, self.colors[topLeft], (coordinates[0], coordinates[1]), (coordinates[0], coordinates[1]+coordinates[3]), lineSize)
        # bottom
        pg.draw.line(surface, self.colors[bottomRight], (coordinates[0], coordinates[1]+coordinates[3]), (coordinates[0]+coordinates[2], coordinates[1]+coordinates[3]), lineSize)
        # right
        pg.draw.line(surface, self.colors[bottomRight], (coordinates[0]+coordinates[2], coordinates[1]), (coordinates[0]+coordinates[2], coordinates[1]+coordinates[3]), lineSize)

    def drawButton(self, surface, x, y, width, height, depth=3, text=None, image=None, sound=None, colors=None, clickButton=0, shading=True, transparent=False, testStr=None):
        buttonRect = pg.Rect(x, y, width, height)
        mouseStatus = self.isClicked(Rect=buttonRect, click=clickButton) # 0: untouched, 1: pressing, 2: hovering, 3: pressed
        pressed = True if mouseStatus == 1 else False
        selected = True if mouseStatus == 3 else False
        # if pressed or selected:
        #     print('pressed: ', pressed, 'selected: ', selected)
        if image != None:
            image = pg.transform.scale(image, (width, height))
            surface.blit(image, (x, y))
        else:
            if not transparent:
                if colors == None:
                    colors = (self.colors['棕'], self.colors['白棕'], self.colors['粉棕']) # untouched, hovering, pressed
                colorIndex = mouseStatus if mouseStatus < 3 else 2
                pg.draw.rect(surface, colors[colorIndex], (x, y, width, height))
        if text != None:
            textSize = 20
            textWidth, textHeight = self.fonts[textSize].size(text)
            while textWidth > width-5:
                textSize -= 1
                textWidth, textHeight = self.fonts[textSize].size(text)
            self.drawText(surface=surface, font=self.fonts[textSize], text=text, color=self.colors['黑'], x=x+(width-textWidth)/2, y=y+(height-textHeight)/2, alpha=255)
        if shading:
            self.drawShading(surface=surface, coordinates=(x, y, width, height), lineSize=depth, pressed=pressed)
        if selected:
            if sound == None:
                self.data.sounds['click 0'].play()
            else:
                sound.play()
        if testStr != None:
            print(testStr, ': ', mouseStatus)
        return selected

    def arrowSelect(self, surface, x, y, width, leftArrowImg, clickedLeftArrowImg, currentIndex, listLength):
        # pos = pg.mouse.get_pos()
        rightArrowImg = pg.transform.flip(leftArrowImg, True, False)
        clickedRightArrowImg = pg.transform.flip(clickedLeftArrowImg, True, False)
        # 箭头按钮碰撞
        leftArrowRect, rightArrowRect = leftArrowImg.get_rect(), rightArrowImg.get_rect()
        leftArrowRect.x, leftArrowRect.y = x, y
        rightArrowRect.x, rightArrowRect.y = x+width, y
        # 渲染左箭头
        if self.isClicked(Rect=leftArrowRect, click=0) == 1:
            surface.blit(clickedLeftArrowImg, (x, y))
        else:
            surface.blit(leftArrowImg, (x, y))
        # 渲染右箭头
        if self.isClicked(Rect=rightArrowRect, click=0) == 1:
            surface.blit(clickedRightArrowImg, (x+width, y))
        else:
            surface.blit(rightArrowImg, (x+width, y))
        if self.isClicked(Rect=leftArrowRect, click=0) == 3:
            self.data.sounds['click 1'].play()
            if currentIndex > 0:
                currentIndex -= 1
            else:
                currentIndex = listLength-1
        if self.isClicked(Rect=rightArrowRect, click=0) == 3:
            self.data.sounds['click 1'].play()
            if currentIndex < listLength-1:
                currentIndex += 1
            else:
                currentIndex = 0
        return currentIndex

    def drawSlideArea(self, surface, x, y, width, height, volume):
        pos = pg.mouse.get_pos()
        lineStartX, lineY = x+width/2-50, y+height/2
        line_Length = 100
        slideRectSize = (20, 32)
        slideRectX, slideRectY = lineStartX+int(line_Length*volume)-slideRectSize[0]/2, lineY-slideRectSize[1]/2
        Rect = pg.Rect(x, y, width, height)
        pg.draw.rect(surface, self.colors['白'], (x, y, width, height))
        pg.draw.line(surface, self.colors['黑'], (lineStartX, lineY), (lineStartX+line_Length, lineY), 2)
        pg.draw.line(surface, self.colors['绿白'], (lineStartX, lineY), (lineStartX+int(line_Length*volume), lineY), 5)
        pg.draw.rect(surface, self.colors['绿白'], (slideRectX, slideRectY, *slideRectSize))

        if self.isClicked(Rect) == 1:
            lineStartX, lineY = x+width/2-50, y+height/2
            if pos[0] >= lineStartX and pos[0] <= lineStartX + line_Length:
                volume = (pos[0]-lineStartX)/line_Length
            else:
                if pos[0] <= lineStartX:
                    volume = 0.0
                else:
                    volume = 1.0
        return volume
    
    def messageBox(self, text, font, bgColor, textColor, width, height):
        pg.draw.rect(self.surface, bgColor, (self.width/2-width/2, self.height/2-height/2, width, height))
        textWidth, textHeight = font.size(text)
        self.drawText(
            font=font, text=text, 
            color=textColor, x=self.width/2-textWidth/2, y=self.height/2-textHeight/2, 
            surface=self.surface, alpha=255
        )

    def displaySaveList(self, x, y, width, height):
        # pg.draw.rect(self.surface, self.colors['棕'], (x, y, width, height))
        if not self.saveList:
            return
        saveLineWidth, saveLineHeight = int(width*0.7), 50
        numPerPage = ((height-100) // saveLineHeight) - 3
        numPerPage = 1 if numPerPage <= 0 else numPerPage
        totalPageNum = len(self.saveList) // numPerPage
        if len(self.saveList) % numPerPage != 0:
            totalPageNum += 1
        # 显示翻页
        leftArrow = pg.transform.scale(self.data.images['left arrow'].convert_alpha(), (16, 16))
        leftArrowClicked = pg.transform.scale(self.data.images['left arrow clicked'].convert_alpha(), (16, 16))
        pageSelectWidth = int(width *0.6)
        arrowX, arrowY = x + width//2 - pageSelectWidth//2, y+20
        self.saveListPage = self.arrowSelect(
            surface=self.surface, x=arrowX, y=arrowY, width=pageSelectWidth, 
            leftArrowImg=leftArrow, clickedLeftArrowImg=leftArrowClicked, 
            currentIndex=self.saveListPage, listLength=totalPageNum
        )
        self.drawText(
            font=self.fonts[15], text=self.data.language['page']+': ', 
            color=self.colors['黑'], x=arrowX-50, y=arrowY, 
            surface=self.surface, alpha=255
        )
        pageText = str(self.saveListPage+1) + '/' + str(totalPageNum)
        pageTextWidth, pageTextHeight = self.fonts[20].size(pageText)
        self.drawText(
            font=self.fonts[20], text=pageText, 
            color=self.colors['黑'], x=arrowX+pageSelectWidth/2-pageTextWidth/2, y=arrowY, 
            surface=self.surface, alpha=255
        )
        # 显示列表
        start = numPerPage * self.saveListPage
        end = len(self.saveList) if len(self.saveList) < start+numPerPage else start+numPerPage
        for i, name in enumerate(self.saveList[start:end]):
            if name == self.chosenSave:
                pg.draw.rect(self.surface, self.colors['白'], (x, arrowY+50+saveLineHeight*i, width, saveLineHeight))
            isClicked = self.drawButton(
                surface=self.surface, x=x+(width-saveLineWidth)/2, y=arrowY+50+saveLineHeight*i, 
                width=saveLineWidth, height=saveLineHeight, 
                depth=0, shading=False, text=name, transparent=True
            )
            if isClicked:
                self.chosenSave = name

    def drawHoldingItem(self):
        if self.data.holdingItem != None:
            item = self.data.holdingItem
            pos = pg.mouse.get_pos()
            midPos = (pos[0]-item.imageSize[item.location][0]/2, pos[1]-item.imageSize[item.location][1]/2)
            self.surface.blit(self.data.holdingItem.img, midPos)

    def addValueWithLimit(self, value, addNum, limit):
        if value < limit:
            value += addNum
            value = limit if value > limit else value
        return value
    
    def minusValueWithLimit(self, value, minusNum, limit):
        if value > limit:
            value -= minusNum
            value = limit if value < limit else value
        return value

    def convertToRawStr(self, s):
        return s.encode('unicode-escape').decode()

    def update(self):
        self.width, self.height = self.currentSize()
        if self.changeScene:
            self.updateVars()
            self.changeScene = False
