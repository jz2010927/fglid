 # -*- coding: utf-8 -*-
from GameObject import GameObject
from Item import Item
import pygame as pg, random, copy

class Merchant(GameObject):
    def __init__(self, data, surface, camera):
        super().__init__(data, surface, camera)
        self.items = []
        self.showMenu = False
        self.selectedItemIndex = 0
        self.fillItemList()

    def updateVars(self):
        super().updateVars()
        self.items = []
        self.showMenu = False
        self.selectedItemIndex = 0
        self.fillItemList()

    def ranEquipment(self, qualityRange=(8, 10)):
        itemAttr = copy.deepcopy(self.data.defaultItemAttr)
        itemAttr['type'] = 0
        itemAttr['quality'] = random.randint(*qualityRange)
        itemAttr['key word'] = random.choice(tuple(self.data.equipmentImgs.keys()))
        itemAttr['random name index'] = 'common name'+str(random.randint(0, 20))
        elements = (
            'qian', 'kun', 'zhen', 'xun', 
            'kan', 'li', 'gen', 'dui'
        )
        element = 'element_' + random.choice(elements)
        minElement, maxElement = itemAttr['quality'], int(itemAttr['quality'] * 99.9)
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
        return itemAttr
    
    def fillItemList(self):
        itemAttr = copy.deepcopy(self.data.defaultItemAttr)
        itemAttr['quality'] = 9
        itemAttr['type'] = 1
        # 1 - 3 升级保护
        itemAttr['key word'] = 'consumable doge'
        for _ in range(3):
            item = Item(data=self.data, surface=self.surface, camera=self.camera, attr=copy.deepcopy(itemAttr))
            item.location = 'merchant'
            self.items.append(item)
        # 4 - 6 答题卡
        itemAttr['key word'] = 'consumable answer sheet'
        for _ in range(3):
            item = Item(data=self.data, surface=self.surface, camera=self.camera, attr=copy.deepcopy(itemAttr))
            item.location = 'merchant'
            self.items.append(item)
        # 7 - 12 装备
        for _ in range(12):
            itemAttr = self.ranEquipment()
            item = Item(data=self.data, surface=self.surface, camera=self.camera, attr=copy.deepcopy(itemAttr))
            item.location = 'merchant'
            self.items.append(item)

    def menu(self):
        # 确定菜单位置
        ui_width, ui_height = 400, 700
        ui_x, ui_y = self.width//2-ui_width//2, self.height//2-ui_height//2
        # 背景
        pg.draw.rect(self.surface, self.colors['灰'], (ui_x, ui_y, ui_width, ui_height))
        # 定价
        if self.items:
            itemAttr = self.items[self.selectedItemIndex].attr
            price = 0
            if itemAttr['key word'] == 'consumable doge':
                price = 1000
            elif itemAttr['key word'] == 'consumable answer sheet':
                price = 5
            else:
                price = 3000
            text = self.data.language['price'] + ' ' + self.data.language['moneyVIP'] + ': ' + str(price) + '/' + str(self.data.playerSave['moneyVIP'])
            textWidth, textHeight = self.fonts[20].size(text)
            textColor = self.colors['绿'] if self.data.playerSave['moneyVIP'] >= price else self.colors['红']
            self.drawText(
                font=self.fonts[20], 
                text=text, 
                color=textColor, 
                x=ui_x+ui_width//2-textWidth//2, y=ui_y+ui_height-110-textHeight, 
                surface=self.surface, alpha=255
            )
        # 选中背景
        if self.items:
            pg.draw.rect(self.surface, self.colors['白'], (ui_x+25+140*(self.selectedItemIndex%3), ui_y+45+90*(self.selectedItemIndex//3), 74, 74))
        for i, item in enumerate(self.items):
            item.x, item.y = ui_x+30+140*(i%3), ui_y+50+90*(i//3)
            # 渲染物品
            item.update()
            # 物品选择按钮
            itemButton = self.drawButton(
                surface=self.surface, x=item.x, y=item.y, 
                width=item.img.get_width(), height=item.img.get_height(), 
                depth=0, text=None, 
                shading=False, transparent=True
            )
            if itemButton:
                self.selectedItemIndex = i
        # 退出
        quit = self.drawButton(
            surface=self.surface, x=ui_x+50, y=ui_y+600, 
            width=100, height=62, 
            depth=3, text=self.data.language['quit'], 
            shading=True
        )
        # 购买
        buy = self.drawButton(
            surface=self.surface, x=ui_x+250, y=ui_y+600, 
            width=100, height=62, 
            depth=3, text=self.data.language['buy'], 
            shading=True
        )
        if quit:
            self.showMenu = False
        if buy and self.items:
            if self.data.playerSave['moneyVIP'] >= price:
                self.data.addItemToBackpack(itemAttr)
                self.data.playerSave['moneyVIP'] -= price
                del self.items[self.selectedItemIndex]
                self.selectedItemIndex = 0
        for item in self.items:
            item.displayAttrHelper()

    def update(self):
        if self.showMenu:
            self.menu()
        super().update()