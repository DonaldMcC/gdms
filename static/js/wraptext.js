// from http://jsfiddle.net/m1erickson/upq6L/

var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");

var text = "'Twas the night before Christmas, when all through the house,  Not a creature was stirring, not even a mouse.  And so begins the story of the day of Christmas";
var font = "12pt verdana";
var textHeight = 15;
var lineHeight = textHeight + 5;
var lines = [];

var cx = 150;
var cy = 150;
var r = 100;

initLines();

wrapText();

ctx.beginPath();
ctx.arc(cx, cy, r, 0, Math.PI * 2, false);
ctx.closePath();
ctx.strokeStyle = "skyblue";
ctx.lineWidth = 2;
ctx.stroke();


// pre-calculate width of each horizontal chord of the circle
// This is the max width allowed for text
// So this just depends on r and creates a lines array from r * .9 down
// Values end up in ctx.filltext - this probably should go into a second version of 
// graphcreator2

function initLines() {

    for (var y = r * .90; y > -r; y -= lineHeight) {

        var h = Math.abs(r - y);

        if (y - lineHeight < 0) {
            h += 20;
        }

        var length = 2 * Math.sqrt(h * (2 * r - h));

        if (length && length > 10) {
            lines.push({
                y: y,
                maxLength: length
            });
        }

    }
}


// draw text on each line of the circle

function wrapText() {

    var i = 0;
    var words = text.split(" ");

    while (i < lines.length && words.length > 0) {

        line = lines[i++];

        var lineData = calcAllowableWords(line.maxLength, words);

        ctx.fillText(lineData.text, cx - lineData.width / 2, cy - line.y + textHeight);

        words.splice(0, lineData.count);
    };

}


// calculate how many words will fit on a line

function calcAllowableWords(maxWidth, words) {

    var wordCount = 0;
    var testLine = "";
    var spacer = "";
    var fittedWidth = 0;
    var fittedText = "";

    //ctx.font = font;

    for (var i = 0; i < words.length; i++) {

        testLine += spacer + words[i];
        spacer = " ";

        //var width = ctx.measureText(testLine).width;
        var width = testline.length * 5;

        if (width > maxWidth) {
            return ({
                count: i,
                width: fittedWidth,
                text: fittedText
            });
        }

        fittedWidth = width;
        fittedText = testLine;

    }
    return ({
                count: i,
                width: fittedWidth,
                text: fittedText
            });
}
