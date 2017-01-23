#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
import time

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
