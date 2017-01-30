#!/usr/bin/env python3
from file.similars_file import SimilarsFile

def main():
    similar = SimilarsFile('kanji.tgz_similars.ut8')
    for kanji in list(similar.kanji):
        # remove index from similar (automatic)
        try:
            similar.kanji[kanji].remove(kanji)
        except:
            pass
        # remove empty/duplicate values (automatic)
        similar_tmp = []
        for s in similar.kanji[kanji]:
            if not s or similar_tmp.count(s):
                print('removed "{}" from {}'.format(s, kanji))
                continue
            similar_tmp.append(s)
        if not len(similar_tmp):
            del similar.kanji[kanji]
            print('removed {} (empty)'.format(kanji))
            continue
        else:
            similar.kanji[kanji] = similar_tmp
        # check for inconsistencies (ask user)
        for s in similar.kanji[kanji]:
            if kanji not in (similar.kanji.get(s) or []):
                while True:
                    print(kanji, ':', similar.kanji.get(kanji))
                    print(s, ':', similar.kanji.get(s))
                    i = input('a(dd) or r(emove) both? ')
                    if i == 'a':
                        if s not in similar.kanji:
                            similar.kanji[s] = []
                        similar.kanji[s].append(kanji)
                    elif i == 'r':
                        similar.kanji[kanji].remove(s)
                        if not len(similar.kanji[kanji]):
                            del similar.kanji[kanji]
                    else:
                        continue
                    break

    similar.write()

if __name__ == '__main__':
    main()
