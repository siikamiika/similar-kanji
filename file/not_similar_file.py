#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
import json

class NotSimilar(object):

    def __init__(self, path='not_similar'):
        self.path = path
        self.not_similar = self._parse()

    def _parse(self):
        try:
            result = OrderedDict()
            for line in open(self.path):
                k, v = line.strip().split(':')
                result[k] = v.split(',')
            return result
        except:
            return OrderedDict()

    def get(self, kanji):
        return self.not_similar.get(kanji) or []

    def write(self):
        with open(self.path, 'w') as f:
            f.write('\n'.join(['{}:{}'.format(
                k, ','.join(self.not_similar[k])) for k in self.not_similar]))


    def add(self, a, b):
        if not self.not_similar.get(a):
            self.not_similar[a] = [b]
        elif not b in self.not_similar[a]:
            self.not_similar[a].append(b)
        if not self.not_similar.get(b):
            self.not_similar[b] = [a]
        elif not a in self.not_similar[b]:
            self.not_similar[b].append(a)
