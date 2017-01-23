# similar-kanji

A machine-readable human-generated file for finding kanji similar to a given kanji and tools to help expand and prune it.

## Format

This project was built around `kanji.tgz_similars.ut8` contained in
[My JWPce](http://ppcenter.webou.net/my_jwpce/) and has the same format.

* Kanji and the kanji similar to it on the same line.
* Forward slash separated list.
* The first kanji is the index and the rest are the kanji similar to it.
* Each line ends with a forward slash because the original file had one as well.
