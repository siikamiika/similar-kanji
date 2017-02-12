var XHR = function(type, path, data, onready, async) {
    if (!onready) {onready = function(){}}
    if (!(async === false)) {async = true};
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            onready(xhr.responseText);
        }
    }

    xhr.open(type, path, async);
    xhr.send(data);
}

var CJK_IDEO_START = 0x4e00;
var CJK_IDEO_END = 0x9faf;

var between = function(n, a, b) {
    return n >= a && n <= b;
}

var isKanji = function(c) {
    return between(c.charCodeAt(0), CJK_IDEO_START, CJK_IDEO_END);
}

///////////////////////////////////////////////////////////////////

var kanjiInput = document.getElementById('kanji-input');
var similarTable = document.getElementById('similar-table');

var tableHeader = '<tr><th>Kanji</th><th>Similar</th></tr>'

kanjiInput.oninput = function() {
    showSimilar(this.value);
}

var similarKanji = {};

XHR('GET', 'https://raw.githubusercontent.com/siikamiika/similar-kanji/master/kanji.tgz_similars.ut8', null, function(data) {
    data = data.match(/[^\n]+/g);
    for (i in data) {
        addLine(data[i]);
    }
    function addLine(line) {
        line = line.match(/[^\/]+/g);
        similarKanji[line[0]] = line.slice(1);
    }
});

function showSimilar(text) {
    var output = [];
    for (i in text) {
        if (isKanji(text[i])) {
            output.push(kanjiInfo(text[i]));
        }
    }

    output = [tableHeader].concat(output.map(function(info) {
        return createTableRow(info);
    }));

    similarTable.innerHTML = output.join('');
}

function kanjiInfo(kanji) {
    return {
        kanji: kanji,
        similar: similarKanji[kanji] || []
    };
}

function createTableRow(info) {
    var output = ['<tr>'];
    output.push('<td style="font-size: 30px;">'+info.kanji+'</td>');
    output.push('<td style="font-size: 24px;">'+info.similar.map(kanjiLink).join(' ')+'</td>');
    output.push('</tr>');
    return output.join('');
}

function kanjiLink(kanji) {
    return '<a href="#" onclick="showSimilar(\''+kanji+'\')">'+kanji+'</a>';
}
