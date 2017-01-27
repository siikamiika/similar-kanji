#!/usr/bin/env python3

import json
from file.similars_file import SimilarsFile
from file.not_similar_file import NotSimilar

class LookalikeBlender(object):

    def __init__(self, original='kanji.tgz_similars.ut8', similar='similar', output='kanji.tgz_similars.ut8'):
        self.original = SimilarsFile(original)
        self.similar = json.load(open(similar))
        self.output = SimilarsFile(output, self.original.kanji)
        self.not_similar = NotSimilar()

    def start(self):
        i = None
        for k in self.similar:
            if i == 'a':
                break
            for lookalike in self.similar[k]['similar']:
                if lookalike == k or lookalike in self.output.get_similar(k) or k in self.not_similar.get(lookalike):
                    continue
                i = input('Do {} and {} look similar? (Y(es)/n(o)/a(bort)):'.format(k, lookalike))
                if i == 'a':
                    break
                if i == 'n':
                    self.not_similar.add(k, lookalike)
                else:
                    self.output.set_similar(k, lookalike)
        self.output.write()
        self.not_similar.write()

if __name__ == '__main__':
    blender = LookalikeBlender()
    blender.start()
