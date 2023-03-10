#!/usr/bin/python
#
# Sprite Sheet Loader - hammythepig
#
# Edited by Peter Kennedy, Kasper Hansen
#
# License - Attribution - hammythepig
    #http://stackoverflow.com/questions/10560446/how-do-you-select-a-sprite-image-from-a-sprite-sheet-in-python
#
# Version = '2.0'

import pygame,sys
from pygame.locals import *

def sprite_sheet(size,file,pos=(0,0)):
    """This cuts sheets into individual sprites one row at a time from left to right."""
    #Initial Values
    len_sprt_x,len_sprt_y = size #sprite size you want
    sprt_rect_x,sprt_rect_y = pos #where to find first sprite on sheet

    sheet = pygame.image.load(file).convert_alpha() #Load the sheet
    sheet_rect = sheet.get_rect()
    sprites = []
    print(sheet_rect.height, sheet_rect.width)
    for i in range(0,sheet_rect.height-len_sprt_y,size[1]):#rows
        for i in range(0,sheet_rect.width-len_sprt_x,size[0]):#columns
            sheet.set_clip(pygame.Rect(sprt_rect_x, sprt_rect_y, len_sprt_x, len_sprt_y)) #find sprite you want
            sprite = sheet.subsurface(sheet.get_clip()) #grab the sprite you want
            sprites.append(sprite)
            sprt_rect_x += len_sprt_x

        sprt_rect_y += len_sprt_y
        sprt_rect_x = 0
    return sprites