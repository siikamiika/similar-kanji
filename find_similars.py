#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import time
import os
import sys
import json
import argparse
from os.path import dirname, realpath
from collections import OrderedDict

os.chdir(dirname(realpath(__file__)))

class Kanjidic2(object):

    def __init__(self):
        self.dicfile = open('kanjidic2.xml', 'rb')
        self.dic = dict()
        self._parse()

    def get(self, kanji):
        dic_entry = self.dic.get(kanji)
        if not dic_entry:
            return

        entry = dict(literal=kanji, on=[], kun=[], nanori=[], meaning=[])

        position, length = dic_entry

        self.dicfile.seek(position)
        character = self.dicfile.read(length)
        character = ET.fromstring(character)

        # stroke count, frequency
        misc = character.find('misc')

        grade = misc.find('grade')
        if grade is not None:
            grade = int(grade.text)
        entry['grade'] = grade

        stroke_count = misc.find('stroke_count')
        if stroke_count is not None:
            stroke_count = int(stroke_count.text)
        entry['stroke_count'] = stroke_count

        freq = misc.find('freq')
        if freq is not None:
            freq = int(freq.text)
        entry['freq'] = freq

        jlpt = misc.find('jlpt')
        if jlpt is not None:
            jlpt = int(jlpt.text)
        entry['jlpt'] = jlpt

        reading_meaning = character.find('reading_meaning')
        if not reading_meaning:
            return
        rmgroup = reading_meaning.find('rmgroup')
        # meaning
        for meaning in rmgroup.iter('meaning'):
            if meaning.get('m_lang') and meaning.get('m_lang') != 'en':
                continue
            entry['meaning'].append(meaning.text)
        # reading
        for reading in rmgroup.iter('reading'):
            r_type = reading.get('r_type')
            if r_type == 'ja_on':
                entry['on'].append(reading.text)
            if r_type == 'ja_kun':
                entry['kun'].append(reading.text)
        # nanori
        for nanori in reading_meaning.iter('nanori'):
            entry['nanori'].append(nanori.text)

        return entry

    def _parse(self):
        print('parsing kanjidic2...')
        start = time.time()

        inside_character = False
        literal = None
        character_start = 0

        while True:
            line = self.dicfile.readline()
            if not line:
                break

            if not inside_character:
                if line == b'<character>\n':
                    inside_character = True
                    character_start = self.dicfile.tell() - len(line)
                    literal = self.dicfile.readline()[9:-11].decode('utf-8')
                continue

            if line == b'</character>\n':
                inside_character = False
                character_position = (character_start, self.dicfile.tell() - character_start)
                self.dic[literal] = character_position

        print('    parsed in {:.2f} s'.format(time.time() - start))


class Radkfile(object):

    SPECIAL_CHAR = {
        'js01': u'⺅',
        'js02': u'𠆢',
        'js07': u'丷',
        '3331': u'⺉',
        'js10': u'𠂉',
        '6134': u'⻌',
        'js04': u'⺌',
        '3D38': u'⺖',
        '3F37': u'⺘',
        '4653': u'⺡',
        '4A6D': u'⺨',
        'js03': u'⺾',
        'kozatoR': u'⻏',
        'kozatoL': u'⻖',
        'js05': u'⺹',
        '4944': u'⺣',
        '504B': u'⺭',
        '4D46': u'疒',
        '5072': u'禸',
        '5C33': u'⻂',
        '5474': u'⺲',
        '3557': u'啇',
        }

    def __init__(self):
        self.file = 'radkfile'
        self.radicals = OrderedDict()
        self.krad = dict()
        self._parse()

    def _parse(self):
        print('parsing radkfile...')
        start = time.time()

        past_comments = False
        radical = None
        index = None
        strokes = None
        kanji = set()
        for l in open(self.file, encoding='euc-jp'):
            if not past_comments:
                if not l.startswith('#'):
                    past_comments = True
                else:
                    continue
            if l.startswith('$'):
                if index:
                    self.radicals[index] = dict(strokes=strokes, kanji=kanji, radical=radical)
                    kanji = set()
                l = l.split()[1:]
                index = l[0]
                radical = self.SPECIAL_CHAR[l[2]] if len(l) == 3 else l[0]
                strokes = int(l[1])
            else:
                l_kanji = list(l.strip())
                kanji.update(l_kanji)
                for k in l_kanji:
                    if not self.krad.get(k):
                        self.krad[k] = set()
                    self.krad[k].add(index)
        self.radicals[index] = dict(strokes=strokes, kanji=kanji, radical=radical)

        print('    parsed in {:.2f} s'.format(time.time() - start))


class SimilarFinder(object):

    def __init__(self, radkfile, kanjidic):
        self.radkfile = radkfile
        self.kanjidic = kanjidic
        self.kanjidic_parsed = dict()
        self.kanji = self._valid_kanji()

    def start(self):
        for kanji1 in self.kanji:
            for kanji2 in self.kanji:
                if self._similar(kanji1, kanji2):
                    self.kanji[kanji1]['similar'].append(kanji2)

        with open('similar', 'w') as f:
            json.dump(self.kanji, f, ensure_ascii=False)

    def _valid_kanji(self):
        valid = dict()
        for k in self.kanjidic.dic:
            kanji = self.kanjidic.get(k)
            if kanji:
                if kanji['grade'] or kanji['freq']:
                    valid[kanji['literal']] = dict(similar=[])
                    self.kanjidic_parsed[k] = kanji
            else:
                print(k)
        print(len(valid))
        return valid

    def _similar(self, kanji1, kanji2):
        kanji1_parts = self.radkfile.krad.get(kanji1)
        kanji2_parts = self.radkfile.krad.get(kanji2)
        if not (kanji1_parts and kanji2_parts):
            return False

        kanji1 = self.kanjidic_parsed[kanji1]
        kanji2 = self.kanjidic_parsed[kanji2]

        strokecount_diff = abs(kanji1['stroke_count'] - kanji2['stroke_count'])

        return len(kanji1_parts ^ kanji2_parts) <= 2 and strokecount_diff <= 2

def main():
    kanjidic2 = Kanjidic2()
    radkfile = Radkfile()
    similar_finder = SimilarFinder(radkfile, kanjidic2)
    similar_finder.start()

if __name__ == '__main__':
    main()
