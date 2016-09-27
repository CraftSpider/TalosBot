/*
    ---------------------
    Chatzy HTML Variables
    ---------------------
*/

var messageTable = "X8414";
var messageContainer = "X4233"
var popup = "X5721";
var messageTime = "X2087";
var messageButton = "X5794";
var PMTag = 'X1046';
var textBox = 'X5999';

/*
    -------------------
    Chatzy JS Variables
    -------------------
*/

var isCleared = "X8614"

/*
    -----------------
    Wrapper Functions
    -----------------
*/

function elementByID(elementID) {
    return document.getElementById(elementID);
}

function elementsByClass(elementClass) {
    return document.getElementsByClassName(elementClass);
}

function leaveChat() {
    X2661('X3836');
}

function closePopup() {
    X8071();
}

function postMessage(message) {
    var HTMLTags = ["<b>", "</b>", "<i>", "</i>", "<s>", "</s>", "<u>", "</u>"];
    var ChatzyTags = ["[b]", "[/b]", "[i]", "[/i]", "[s]", "[/s]", "[u]", "[/u]"];
    for (var tag in HTMLTags) {
        message = message.replace(HTMLTags[tag],ChatzyTags[tag]);
    }
    X4727(message);
}

function closeChat() {
    postMessage("/close");
}

function openChat() {
    postMessage("/open");
}

function toggleChatLock() {
    if(X5170.X5289) { //Variable for whether the chat is locked, of course.
        postMessage("/open");
    } else {
        postMessage("/close");
    }
}

function searchMessages(term, poster) {
    postMessage("/find " + (poster?"{V:" + poster + "} ":"") + (term?term:""));
}

function privateMessage(name, message) {
    postMessage("/pm \"" + name + "\" " + message);
}

function globalMessage(message) { //Note, only sends the message to online users.
    var users = X3884.split("\n");
    for (var i = 1; i <= users[0]; i++) {
        user = users[i].split(" ");
        privateMessage(user[0], message);   //Replace the 0 with other numbers to grab different values. 2 is last leave/exit, 4 is status, 5 is location.
    }
}

function editRoomBoard(message, method, key) {  //Method is the style of editing to use. Options are: 0/default, overwrite. 1, append. 2, prepend. 3, replace.
    postMessage("/rb");
    setTimeout(function() {
        var BoardMessage = elementByID("X6196");
        switch (method) {
            case 1:
                BoardMessage.value = BoardMessage.value + "\n" + message;
                break;
            case 2:
                BoardMessage.value = message + "\n" + BoardMessage.value;
                break;
            case 3:
                if (BoardMessage.value.match(new RegExp(key, "g")).length > 1) {
                    BoardMessage.value = BoardMessage.value.replace(new RegExp(key + ".+?" + key, "g"), key + message + key);
                }
                break;
            default:
                BoardMessage.value = message;
        }
        X565.onclick();
    }, 150);
}

//Requires Re-Init. Fix that?
function changeName(name) {
    X8752('X6610');

    setTimeout(function() {
        X4964.value = name;
        X2575.onsubmit();
    }, 1000);
}

function highlightTab(elIn, classIn, confusingBool) {
    var hasClass = new RegExp("\\b" + classIn + "\\b");
    if (!confusingBool != !elIn.className.match(hasClass)) { //This is just a XOR. Combined with the bellow if, it means that this is checking whether we are adding or removing a class, and if that is necessary.
        if (confusingBool) {
            elIn.className += (elIn.className ? " " : "") + classIn;
        } else {
            elIn.className = elIn.className.replace(hasClass, "").replace(/^\s/, "").replace(/\s$/, "");
        }
    }
}

function generateTab(picName, clickFunc, displayText, isChecked, isLocked) {
    return '<A href="#" onClick="' + clickFunc + 'return false;"' + (isLocked ? ' class="X8949"' : "") + '>' + (isChecked ? "<SPAN style='float:right;margin:0 4px 0 0;'>&nbsp;&#10003;</SPAN>" : "") + (picName ? '<IMG src="/elements/icon17/' + picName + '.png">' : "") + displayText + '</A>';
}
