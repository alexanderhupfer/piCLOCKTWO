#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
import pygame, sys, os
import pygame.gfxdraw
import xmltodict
#from yr.libyr import Yr
from pygame.locals import *
import sys
import subprocess

if sys.argv[-1] == 'stop':
    exit()

out = subprocess.check_output("ls /sys/bus/w1/devices", shell=True)
global sensor1_id
sensor1_id = out.split('\n')[0]

url = "https://api.forecast.io/forecast/91edcb26bf4bf674333e73905762e7f4/59.9207260,10.7365420"
urlmetno = "http://api.met.no/weatherapi/locationforecast/1.9/?lat=59.9207260;lon=10.7365420"

def get_temp_w1():
    out = subprocess.check_output("tail -n1 /sys/bus/w1/devices/%s/w1_slave" % sensor1_id, shell=True)
    temp_str = out.split()[-1][2:]
    temp = float(temp_str) / 1000.
    tempstring = u'%s˚' % round(temp,1)
    return tempstring

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
        tempstring = u'%s˚' % round(temp,1)
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
    face = u'''ESkISTaFÜNF
ZEHNZWANZIG
DREIVIERTEL
VORfunkNACH
HALBAELFÜNF
EINSxämZWEI
DREIaujVIER
SECHSmlACHT
SIEBENZWÖLF
ZEHNEUNkUHR'''

    hour = localtime.tm_hour
    minute = localtime.tm_min
    #hour = 1
    #minute = 2
    minute -= minute % 5
    highlights = []
    highlights.append(u'ES')
    highlights.append(u'IST')
    minutes = {0:[u'UHR'],
               5:[u'FÜNF',u'NACH'],
               10:[u'ZEHN',u'NACH'],
               15:[u'VIERTEL',u'NACH'],
               20:[u'ZWANZIG',u'NACH'],
               25:[u'FÜNF',u'VOR',u'HALB'],
               30:[u'HALB'],
               35:[u'FÜNF',u'NACH',u'HALB'],
               40:[u'ZEHN',u'NACH',u'HALB'],
               45:[u'DREIVIERTEL'],
               50:[u'ZEHN',u'VOR'],
               55:[u'FÜNF',u'VOR']}
    hours = {0:u'ZWÖLF',
             1:u'EINS',
             2:u'ZWEI',
             3:u'DREI',
             4:u'VIER',
             5:u'FÜNF',
             6:u'SECHS',
             7:u'SIEBEN',
             8:u'ACHT',
             9:u'NEUN',
             10:u'ZEHN',
             11:u'ELF'}

    if minute == 0:
        hours.update({1:u'EIN'})
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


    text = tfont.render(get_temp_w1(), 1, WHITE)
    textpos = text.get_rect()
    textpos.right = 310
    textpos.centery = 70
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
