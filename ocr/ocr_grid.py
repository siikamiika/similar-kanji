#!/usr/bin/env python3
import sys
import os
import json
import base64
from io import BytesIO
from collections import OrderedDict
import pyocr
import pyocr.builders
from PIL import Image, ImageFilter

tool = pyocr.get_available_tools()[0]
SINGLE_CHAR = 10

PREV_DIGIT = 0
global PREV_DIGIT

def ocr_grid_cell(img, position, step, mode):
    global PREV_DIGIT
    x_1, y_1 = [position[i] * step[i] + 15 for i in range(2)]
    x_2, y_2 = [(position[i] + 1) * step[i] - 15 for i in range(2)]
    img = img.crop((x_1, y_1, x_2, y_2)).convert('1')
    if mode == 'char':
        text = tool.image_to_string(
            img,
            lang='jpn',
            builder=pyocr.builders.TextBuilder(SINGLE_CHAR)
        )
    elif mode == 'digit':
        #if PREV_DIGIT < 9:
        #    layout = SINGLE_CHAR
        #else:
        layout = 3
        text = int(tool.image_to_string(
            img,
            builder=pyocr.tesseract.DigitBuilder(layout)
        ).strip().replace('O', '0') or -1)
        if text != -1:
            PREV_DIGIT = text
    print(position, text)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    #img.save('cell_{}_{}.png'.format(position[0], position[1]))
    return text, base64.b64encode(buffer.getvalue()).decode('utf-8')

def main():
    filename = sys.argv[1]
    img = Image.open(filename)
    # crop
    img = img.crop(tuple(map(int, sys.argv[2].split(','))))
    # grid
    grid_w, grid_h = map(int, sys.argv[3].split('x'))

    width, height = img.size
    print(width, height)
    x_step = width / grid_w
    y_step = height / grid_h
    print(x_step, y_step)

    grid_text = []
    for x in range(grid_w):
        grid_text.append([])
        for y in range(grid_h):
            grid_text[x].append(ocr_grid_cell(
                img,
                (x, y),
                (x_step, y_step),
                'char' if x % 2 else 'digit'
                ))

    similar = OrderedDict()
    similar_idx = 0 if len(sys.argv) < 5 else int(sys.argv[4])
    if similar_idx:
        similar[similar_idx] = []

    for column in range(1, len(grid_text), 2):
        for cell_index in range(len(grid_text[column])):
            if grid_text[column - 1][cell_index][0] != -1:
                similar_idx = grid_text[column - 1][cell_index][0]
                similar[similar_idx] = []

            similar[similar_idx].append(grid_text[column][cell_index])

    with open(filename + '.json', 'w') as f:
        json.dump(similar, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
