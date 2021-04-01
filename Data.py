 # -*- coding: utf-8 -*-
import json, os, pickle, sys, pygame as pg, threading, copy
from win32api import GetSystemMetrics

class Data:
    def __init__(self):
        self.osPath = os.path.join
        self.path = {
            'settings': self.osPath('settings', 'settings.json'), 
            'save': self.osPath('save'), 
            'language': self.osPath('languages'), 
            'images': self.osPath('assets', 'images'), 
            'sounds': self.osPath('assets', 'audios'), 
            'fonts': self.osPath('assets', 'fonts')
        }
        self.defaultSettings = {
            "language": "zhCN", "resolution": [GetSystemMetrics(0), GetSystemMetrics(1)-64], "fps": 60, "camera speed": 30, "sound volume": [0.5, 0.5, 0.5], "full screen": False, 
            'key bindings': {'up': pg.K_w, 'down': pg.K_s, 'left': pg.K_a, 'right': pg.K_d, 'backpack': pg.K_v, 'player attributes': pg.K_c, 'settings': pg.K_ESCAPE}
        }
        self.defaultPlayerSave = {
            'name':'', 'profile image': None,
            'level': 1, 
            'main base level': 0, 
            'current exp': 0, 'levelup exp':1, 'exp multiplier': 1.0, 
            'current hp': 100, 'max hp': 100, 'hp recovery': 1, 
            'knowledge level': 0, 'knowledge exp': 0, 'knowledge levelup exp': 1, 
            'attack': 10,  
            'defense': 10,  
            'critical chance': 0.1, 
            'critical multiplier': 1.2, 
            'attack speed': 300, 
            'move speed': 10, 
            'attack range': 500,  
            'dodge chance': 0.1, 
            'element_qian': 10, 'element_kun': 10, 'element_zhen': 10, 'element_xun': 10, 
            'element_kan': 10, 'element_li': 10, 'element_gen': 10, 'element_dui': 10, 
            'money0': 500, 'money1': 500, 'money2': 500, 'money3': 500, 'money4':500, 'moneyVIP': 100, 
            'equipment': [None]*10, 
            'backpack': [], 
            'warehouse':[], 'rookie': True, 'cards': {}, 
            'item recycle': None, 'item level upgrade': None, 'item star upgrade': None
        }
        backpack1Page = [None] * 60
        for _ in range(100):
            self.defaultPlayerSave['backpack'].append(copy.deepcopy(backpack1Page))
        self.playerTotalValues = {
            'exp multiplier': 1.0, 'max hp': 10000, 'hp recovery': 1, 'attack': 0, 'defense': 1, 
            'critical chance': 0.5, 'critical multiplier': 1.5, 'attack speed': 10, 'move speed': 10, 
            'attack range': 1, 'dodge chance': 0.1,
            'element_qian': 0, 'element_kun': 0, 'element_zhen': 0, 'element_xun': 0, 
            'element_kan': 0, 'element_li': 0, 'element_gen': 0, 'element_dui': 0
        }
        self.defaultItemAttr = {
            'key word': '', 
            'random name index': None, 'name': '', 
            'amount': 0, 'icon star': 0, 
            'quality': 0, 'level': 0, 
            'attack': 0, 'defense': 0, 
            'dodge chance': 0.0, 'attack range': 0, 
            'critical chance': 0.0, 'critical multiplier': 0.0, 
            'attack speed': 0, 'move speed': 0, 
            'hp': 0, 'hp percent': 0.0, 'max hp': 0, 'hp recovery': 0, 
            'exp': 0, 'exp percent': 0.0, 'exp multiplier': 0.0, 'required level': 0, 
            'element_qian': 0, 'element_kun': 0, 'element_zhen': 0, 'element_xun': 0, 
            'element_kan': 0, 'element_li': 0, 'element_gen': 0, 'element_dui': 0, 
            'description': '', 'sockets': [], 'socket number': 0, 'type': 0, 'element': 'element_qian'
        }
        self.defaultMonster = {
            'name': '', 'quality': 0, 'level': 0, 'exp': 10, 
            'attack': 1, 'defense': 0, 'attack speed': 2, 
            'dodge chance': 0.3, 'move speed': 5, 'hp': 200, 'type': 0, 
            'element_qian': 1, 'element_kun': 1, 'element_zhen': 1, 'element_xun': 1, 
            'element_kan': 1, 'element_li': 1, 'element_gen': 1, 'element_dui': 1, 
            'element': None
        }
        self.gameAttrRange = {
            'user level range': (1, 999), 'user hp range': (100, 9999999999), 'user money range': (0, 999999999999999999999), 
            'user maxHp range': (100, 9999999999), 'user knowledge level range': (0, 20), 'user attack speed range': (0, 999), 
            'user move speed range': (1, 30), 'user max range': 1000, 
            'warehouse capacity': 1000, 'item star range': (0, 9), 'item quality range': (0, 10), 'item level range': (0, 99), 
            'item socket number range': (0, 6), 'element range': (0, 999999), 'main base level range': (0, 999)
        }
        self.playerChanged = False
        self.settings = self.loadSettings()
        self.languageList = self.loadLanguageList()
        self.language = self.loadLanguage()
        self.colors = {
            '红': (255, 0, 0), '绿': (0, 255, 0), '蓝': (0, 0, 255), 
            '绿2': (35, 205, 182), '绿白': (142, 229, 213), '白绿蓝': (148, 251, 240), 
            '白蓝': (192, 247, 252), '白绿': (172, 248, 211), '白棕': (230, 228, 192), 
            '棕': (231, 202, 127), '粉': (255, 215, 187), '肉': (255, 179, 168), 
            '红粉': (255, 76, 108), '绿蓝': (42, 224, 200), '蓝绿': (162, 225, 212), 
            '白蓝绿': (172, 246, 239), '白蓝2': (203, 245, 251), '白绿2': (189, 243, 212), 
            '白棕2': (230, 226, 195), '棕白': (227, 200, 135), '粉肉': (250, 216, 190), 
            '肉粉': (251, 184, 172), '红粉2': (254, 102, 115), '白绿3': (199, 237, 204), 
            '粉棕': (236, 212, 197), '黑': (0, 0, 0), '白': (255, 255, 255), 
            '金':(255, 215, 0) , '黄2': (240, 230, 140), '黄3': (218, 165, 32), 
            '金2': (255, 223, 0), '黄绿': (173, 255, 47), '黄绿2': (154, 205, 50), 
            '紫': (160, 32, 240), '淡紫': (218, 112, 214), '紫罗兰': (138, 43, 226), 
            '湖紫': (153, 51, 250), '梅红': (221, 160, 221), '灰': (192, 192, 192), 
            '桔': (255, 128, 0), '粉红': (255, 192, 203), '雪白': (255, 250, 250), 
            '靛蓝': (81, 151, 151), '绿3': (0, 120, 0),
        }
        mainRes = ((800, 600), (1024, 768), (1200, 800), (1200, 900), (1280, 720), (1280, 1024), 
            (1366, 768), (1440, 900), (1600, 900), (1680, 1050), (1920, 1080), (1920, 1200), (2560, 1440), 
            (2560, 1600), (3840, 2160), (7680, 4320))
        self.resolutionList = sorted([r for r in mainRes if r[0]<=GetSystemMetrics(0) and r[1]<=GetSystemMetrics(1)]) if not self.settings['full screen'] else sorted(mainRes)
        self.fpsList = (60, 72, 75, 120, 144, 240)
        self.images = {}
        self.sounds = {}
        self.fonts = None
        self.qualityColor = (
            self.colors['灰'], # 0
            self.colors['白'], 
            self.colors['白蓝'], 
            self.colors['绿蓝'], 
            self.colors['绿'], 
            self.colors['黄绿'], 
            self.colors['梅红'], 
            self.colors['淡紫'], 
            self.colors['湖紫'], 
            self.colors['金'], 
            self.colors['肉'] # 10
        )
        self.holdingItem, self.holdFromPlace = None, {'place':'backpack', 'page':None, 'index':0}
        self.mainbaseItem = {'recycle': None, 'level upgrade': None, 'star upgrade': None}
    
    def loadAssetsToRam(self):
        # load self.images
        self.loadHelper(jsonFileName='imageList', threads=8)
        # load self.sounds
        self.loadHelper(jsonFileName='soundList', threads=8)
        # 设置音量
        for k,v in self.sounds.items():
            if 'bgm' in k:
                v.set_volume(self.settings['sound volume'][0] * self.settings['sound volume'][1])
            else:
                v.set_volume(self.settings['sound volume'][0] * self.settings['sound volume'][2])
        self.fonts = [pg.font.Font(os.path.join('assets', 'fonts', '1.ttf'), i) for i in range(1, 73)]
        self.fonts2 = [pg.font.Font(os.path.join('assets', 'fonts', '2.ttf'), i) for i in range(1, 73)]
        self.elementImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:8]=='element_'}
        self.qualityBgImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:10]=='quality bg'}
        self.equipmentImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:10]=='equipment '}
        self.consumableImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:11]=='consumable '}
        self.pokerCardImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:5]=='card_'}
        self.buildingImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:9]=='building '}
        self.moneyImgs = {name:img.convert_alpha() for name, img in self.images.items() if name[:5]=='money' and 'VIP' not in name}
        self.defaultPlayerSave['cards'] = {name:0 for name in self.pokerCardImgs.keys()}
        self.playerSave = copy.deepcopy(self.defaultPlayerSave)

    def loadLanguage(self):
        lan = {}
        path = self.osPath(self.path['language'], self.settings['language']+'.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lan = json.load(f)
        except :
            print(path+' not found!!!')
            return None
        return lan

    def loadAssetsFromDict(self, pathDict, fileType):
        #fileType 0 image, 1 sounds
        loadMethods = (pg.image.load, pg.mixer.Sound)
        dictContainer = (self.images, self.sounds)
        assets = {}
        for name, filePath in pathDict.items():
            try:
                assets[name] = loadMethods[fileType](filePath)
            except:
                print(name, ': ', filePath)
        dictContainer[fileType].update(assets)

    def loadHelper(self, jsonFileName, threads=4):
        filePaths = None
        assetPaths = {}
        typeDict = {'imageList': 0, 'soundList': 1}
        path = self.osPath('assets', jsonFileName+'.json')
        if not os.path.exists(path):
            print(path+' not found!!!')
            return None
        with open(path, 'r', encoding='utf-8') as f:
            assetPaths = json.load(f)
        rootPath = assetPaths['root']
        del assetPaths['root']
        realPaths = {k:self.osPath(*rootPath, *v) for k,v in assetPaths.items()}
        filePaths = list(realPaths.items())
        pathLength = len(filePaths)
        if pathLength > threads:
            Ts = []
            slicedLength = pathLength // threads
            start = 0
            end = start + slicedLength
            for i in range(threads):
                pathDict = dict(filePaths[start:end])
                if i == threads-1:
                    pathDict = dict(filePaths[start:])
                t = threading.Thread(target=self.loadAssetsFromDict, args=(pathDict, typeDict[jsonFileName],))
                Ts.append(t)
                t.start()
                start = end
                end += slicedLength
            for t in Ts:
                t.join()
        else:
            self.loadAssetsFromDict(pathDict=realPaths, fileType=typeDict[jsonFileName])

    def setVolumes(self):
        pg.mixer.music.set_volume(self.settings['sound volume'][0] * self.settings['sound volume'][1])
        for sound in self.sounds.values():
            sound[0].set_volume(self.settings['sound volume'][0] * self.settings['sound volume'][sound[1]])

    def saveSettings(self):
        Dir = os.path.join('settings')
        if not os.path.isdir(Dir):
            self.settings = self.defaultSettings
            os.makedirs(Dir)
        path = os.path.join(Dir, 'settings.json')
        try:
            with open(path, 'w') as f:
                json.dump(self.settings, f)
                print(path, ' saved')
        except :
            print(path, ' save failed')
            return False
        return True

    def loadSettings(self):
        path = os.path.join('settings', 'settings.json')
        if not os.path.isfile(path):
            print(path, ' not found')
            return copy.deepcopy(self.defaultSettings)
        try:
            with open(path, 'r') as f:
                settings = json.load(f)
        except :
            print(path, ' loadinig error')
            return copy.deepcopy(self.defaultSettings)
        return settings
    
    def save(self, name):
        if not os.path.isdir('save'):
            os.makedirs('save')
        path = os.path.join('save', name+'.cundang')
        # try:
        with open(path, 'wb') as handle:
            pickle.dump(self.playerSave, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(path, ' saved')
        return True
        # except:
        #     print('Save ', path, ' failed')
        #     return False
    
    def load(self, name):
        path = os.path.join('save', name+'.cundang')
        try:
            with open(path, 'rb') as handle:
                self.playerSave = pickle.load(handle)
            print(path, ' loaded')
            return True
        except:
            print(path, ' load failed')
            return False

    def loadSaveList(self):
        return [f[0:-8] for f in os.listdir('save') if f[-8:]=='.cundang']
    
    def loadLanguageList(self):
        languageList = {}
        try:
            with open(os.path.join('languages', 'list.json'), 'r', encoding='utf-8') as f:
                languageList = json.load(f)
        except: 
            print("Unexpected error:", sys.exc_info()[0])
            raise
        return languageList

    def updateSpace(self, place):
        if place == 'backpack':
            inventory = [item for sublist in self.playerSave['backpack'] for item in sublist if item == None]
        elif place == 'equipment':
            inventory = [item for item in self.playerSave['equipment'] if item == None]
        return len(inventory)

    def countItemInBag(self, keyWord):
        n = 0
        for p in self.playerSave['backpack']:
            for i in p:
                if i != None:
                    if keyWord in i['key word']:
                        n += 1
        return n
        
    def deleteItemFromBag(self, keyWord, maxNum):
        for p in range(len(self.playerSave['backpack'])):
            for i in range(len(self.playerSave['backpack'][p])):
                itemAttr = self.playerSave['backpack'][p][i]
                if itemAttr != None and maxNum > 0:
                    if keyWord in itemAttr['key word']:
                        self.playerSave['backpack'][p][i] = None
                        maxNum -= 1

    def addItemToBackpack(self, attr):
        for p in range(len(self.playerSave['backpack'])):
            for i in range(len(self.playerSave['backpack'][p])):
                if self.playerSave['backpack'][p][i] == None:
                    self.playerSave['backpack'][p][i] = attr
                    return
    
    def stopSound(self):
        for sound in self.sounds.values():
            sound.stop()

if __name__ == '__main__':
    d = Data()