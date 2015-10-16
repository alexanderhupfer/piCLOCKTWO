import time
import requests
import pygame, sys, os
import pygame.gfxdraw
import xmltodict
#from yr.libyr import Yr
from pygame.locals import *
import sys

if sys.argv[-1] == 'stop':
    exit()

url = "https://api.forecast.io/forecast/91edcb26bf4bf674333e73905762e7f4/59.9207260,10.7365420"
urlmetno = "http://api.met.no/weatherapi/locationforecast/1.9/?lat=59.9207260;lon=10.7365420"

def get_temp_metno():
    xml = requests.get(urlmetno).text
    data = xmltodict.parse(xml)
    temperatures = []
    for t in data['weatherdata']['product']['time']:
        try:
            temperatures.append(float(t['location']['temperature']['@value']))
        except KeyError:
            pass
    return temperatures

def get_temp_forecastio():
    temperatures = []
    json = requests.get(url).json()
    for t in json['hourly']['data']:
        f = t['apparentTemperature']
        t = (f - 32) * 5.0/9.0
        temperatures.append(t)
    return temperatures
    

class Weather(object):
    def __init__(self):
        self.refreshed_this_hour = False
    def refresh(self):
        mins = time.gmtime().tm_min
        if mins < 1:
            self.refreshed_this_hour = False
        if mins >= 1 and not self.refreshed_this_hour:
            self.get_forecast()
            self.refreshed_this_hour = True
        t = mins/60.
        t0 = self.data[0]
        t1 = self.data[1]
        temp = t0*(1-t) + t1*t
        tempstring = '%s˚' % round(temp,1)
        return tempstring

    def get_forecast(self):
        print('api querry...')
        #self.data = get_temp_forecastio()
        self.data = get_temp_metno()



os.environ["SDL_FBDEV"] = "/dev/fb1"
# Uncomment if you have a touch panel and find the X value for your device
#os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.environ["SDL_MOUSEDEV"] = "/dev/input/eventX"

def get_time_string(localtime):
    face = '''ESkISTaFÜNF
ZEHNZWANZIG
DREIVIERTEL
VORfunkNACH
HALBAELFÜNF
EINSxämZWEI
DREIaujVIER
SECHSmlACHT
SIEBENZWÖLF
ZEHNEUNkUHR'''

    hour = localtime.tm_hour + 2
    minute = localtime.tm_min
    #hour = 1
    #minute = 2
    minute -= minute % 5
    highlights = []
    highlights.append('ES')
    highlights.append('IST')
    minutes = {0:['UHR'],
               5:['FÜNF','NACH'],
               10:['ZEHN','NACH'],
               15:['VIERTEL','NACH'],
               20:['ZWANZIG','NACH'],
               25:['FÜNF','VOR','HALB'],
               30:['HALB'],
               35:['FÜNF','NACH','HALB'],
               40:['ZEHN','NACH','HALB'],
               45:['DREIVIERTEL'],
               50:['ZEHN','VOR'],
               55:['FÜNF','VOR']}
    hours = {0:'ZWÖLF',
             1:'EINS',
             2:'ZWEI',
             3:'DREI',
             4:'VIER',
             5:'FÜNF',
             6:'SECHS',
             7:'SIEBEN',
             8:'ACHT',
             9:'NEUN',
             10:'ZEHN',
             11:'ELF'}

    if minute == 0:
        hours.update({1:'EIN'})
    for m in minutes[minute]:
        highlights.append(m)
    if minute >= 25:
        hour += 1
    hour = hour % 12
    positions = []
    for h in highlights:
        positions.append(face.index(h))
    positions.append(len(face) - face[::-1].index(hours[hour][::-1]) - len(hours[hour]))
    highlights.append(hours[hour])
    face = face.lower()
    face = list(face)
    for p, h in zip(positions,highlights):
        face[p:p+len(h)] = list(h)
    return ''.join(face)

pygame.init()

# set up the window
DISPLAYSURF = pygame.display.set_mode((320, 240), 0, 32)
pygame.mouse.set_visible(False)
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GRAY  = (70 , 70 ,  70)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

#weather = Yr(location_name='Norway/Oslo/Oslo/Oslo')
#textcontent = weather.now()['temperature']['@value'] + '°'
#stime = time.time()
#nextrefresh = stime + 3600/4

def get_positions(height, width, centerx, centery):
    positions = []
    for i in range(10*12):
        x = i % 12
        xpos = (x / 11.)*width - 0.5 * width + centerx
        y = (i - x)/12
        ypos = (y / 10.)*height - 0.5 * height + centery
        positions.append((xpos, ypos))
    return positions

positions = get_positions(220, 200, 320-200, 260/2)


def draw_circle(x,y, color):
    pygame.gfxdraw.filled_circle(DISPLAYSURF, x, y, 4, color)
    pygame.gfxdraw.aacircle(DISPLAYSURF, x, y, 4, color)
    pygame.gfxdraw.aacircle(DISPLAYSURF, x, y, 5, color)


weather = Weather()

while True:
    DISPLAYSURF.fill(BLACK)
    font = pygame.font.SysFont("helvetica", 20)
    tfont = pygame.font.SysFont("helvetica", 40)


    text = tfont.render(weather.refresh(), 1, WHITE)
    textpos = text.get_rect()
    textpos.right = 310 
    textpos.centery = 30
    DISPLAYSURF.blit(text, textpos)

    localtime = time.localtime()

    time_string = get_time_string(time.localtime())
    for t, p in zip(time_string, positions):
        if t == '\n':
            continue
        if t.islower():
            t = t.upper()
            text = font.render(t, 1, GRAY)
        else:
            text = font.render(t, 1, WHITE)
        textpos = text.get_rect()
        textpos.centerx = p[0] 
        textpos.centery = p[1]
        DISPLAYSURF.blit(text, textpos)


    minutesx = 237
    minutesy = 217
    x = 20

    if localtime.tm_min % 5 > 0:
        draw_circle(minutesx, minutesy, WHITE)
    else: 
        draw_circle(minutesx, minutesy, GRAY)

    if localtime.tm_min % 5 > 1:
        draw_circle(minutesx+x,minutesy, WHITE)
    else:
        draw_circle(minutesx+x, minutesy, GRAY)

    if localtime.tm_min % 5 > 2:
        draw_circle(minutesx+x+x,minutesy, WHITE)
    else:
        draw_circle(minutesx+x+x,minutesy, GRAY)

    if localtime.tm_min % 5 > 3:
        draw_circle(minutesx+x+x+x,minutesy, WHITE)
    else:
        draw_circle(minutesx+x+x+x,minutesy, GRAY)



    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    time.sleep(1)
