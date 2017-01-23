#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict

class SimilarsFile(object):

    def __init__(self, path, base=None):
        self.path = path
        if base:
            self.kanji = OrderedDict(base)
        else:
            self._parse()

    def _parse(self):
        self.kanji = OrderedDict()
        with open(self.path, 'r') as f:
            lines = f.read().splitlines()
        for l in lines:
            l = [k for k in l.split('/') if k.strip()]
            self.kanji[l[0]] = l[1:]

    def write(self):
        lines = ['{}/{}/'.format(c, '/'.join(self.kanji[c])) for c in self.kanji]
        with open(self.path, 'w') as f:
            f.write('\n'.join(lines) + '\n')

    def get_similar(self, char):
        return self.kanji.get(char) or []

    def set_similar(self, char, similar):
        if char not in self.kanji:
            self.kanji[char] = []
        if similar not in self.kanji[char]:
            self.kanji[char].append(similar)
        if similar not in self.kanji:
            self.kanji[similar] = []
        if char not in self.kanji[similar]:
            self.kanji[similar].append(char)

    def remove_similar(self, char, similar):
        try:
            self.kanji[char].remove(similar)
        except (KeyError, ValueError):
            pass

        try:
            self.kanji[similar].remove(char)
        except (KeyError, ValueError):
            pass
