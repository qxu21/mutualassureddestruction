//this is the first line of javascript ever written in Mutual Assured Destruction. For posterity, it shall never be deleted.

function expandMessage(event) {
    var message = this.nextSibling; //hopefully i can modify this
    if (message.getAttribute("display") === "none") {
        message.setAttribute("display", "initial");
    } else {
        message.setAttribute("display", "none");
    }
}

var trs = Document.querySelectorAll(".messageheader")
for (var tr of trs) { //var x in y would be "0" "1" "2"...
    tr.onclick = expandMessage;
}

