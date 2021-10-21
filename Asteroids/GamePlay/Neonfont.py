#fell down a cv2 rabbit hole but eventually came up from air and created this version of a gaussian blur neon look using PIL
#https://stackoverflow.com/questions/67561142/bloom-effect-in-pygame-so-that-text-glows
#https://stackoverflow.com/questions/37191008/load-truetype-font-to-opencv

import pygame

from PIL import ImageFont, Image, ImageDraw, ImageFilter
import os

font_file = os.path.join(os.path.dirname(__file__), 'Hyperspace_Bold.otf')

def convert_to_image(text, fontSize, screenSize):
    """repacks font to an image"""
    font = ImageFont.truetype(font_file, fontSize) #font instructions
    img = Image.new('RGBA', screenSize, color = (255, 255, 255, 0)) #image instructions
    draw = ImageDraw.Draw(img) #draw onto the image
    #do so several times a little off center to make it bolder
    draw.text((10, 10), text, font=font)
    draw.text((11, 10), text, font=font)
    draw.text((10, 11), text, font=font)
    draw.text((11, 11), text, font=font)
    draw.text((11, 12), text, font=font)
    draw.text((12, 11), text, font=font)
    draw.text((12, 12), text, font=font)
    return img

def create_blur(text, fontSize, screenSize):
    """adds a gaussian blur to the image"""
    image = convert_to_image(text, fontSize, screenSize) #passes the text to convert the image
    img = image.filter(ImageFilter.GaussianBlur(radius = 4)) #blurs it
    return img

def apply_blur(text, fontSize, screenSize):
    """apply the blur under the text"""
    image = create_blur(text, fontSize, screenSize)
    font = ImageFont.truetype(font_file, fontSize)
    img = image
    draw = ImageDraw.Draw(img) #redraws a second clear copy of the gaussian blur
    draw.text((11, 11), text, font=font)
    return img

def set_image(text, font_size):
    """turns the blurred image into a pygame image"""
    image = apply_blur(text, font_size, (200, 100))
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode)