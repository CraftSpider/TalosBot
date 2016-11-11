/*
    ------------------
    Initialize Variables
    ------------------
*/

//Constants
const VERSION = 1.4;
const BOOT_TIME = new Date();
const WH_TIME = 0;
const ADMINS = ["Dino", "α|CraftSpider|Ω", "HiddenStorys", "wundrweapon"];
const URL = "http://rawgit.com/CraftSpider/TalosBot/Command/";

//Control variables
var CommandsLoaded = false;

//Writing Hour variables
var WHSwitch = 0;

/*
    -------------------
    Arbitrary functions
    -------------------
*/

function randomNumber(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

function startWW(length, KeyWord) {
    setTimeout(function() {
        NumWWs--;
        if (!IsSleeping) {
            postMessage("[b]Word War " + (KeyWord? "'" + KeyWord + "' " : "") + "ends.[/b] How did you do?");
        }
    }, length * 60000);
}

function parseArgs(str) {
    var out = [];
    
    if (str.match(/".*?"/)) {
        var delim = false;
        var arg = "";
        for (var char in str) {
            if (str[char] == "\"") {
                delim = !delim;
                if (arg) {
                    out.push(arg);
                    arg = "";
                }
            } else if (str[char] == " " && !delim) {
                if (arg) {
                    out.push(arg);
                    arg = "";
                }
            } else {
                arg += str[char];
            }
        }
        if (arg) {
            out.push(arg);
        }
    } else {
        out = str.split(/\s/);
    }
    
    return out;
}

function stringify(object) {
    return JSON.stringify(object);
}

function parse(string) {
    return JSON.parse(string);
}

function setStorage(key, content) {
    window.localStorage[key] = content;
}

function getStorage(key) {
    return window.localStorage[key];
}

function removeStorage(key) {
    oldItem = getStorage(key);
    window.localStorage.removeItem(key);
    return oldItem;
}

function makeElement(name, attrs) {
    ele = document.createElement(name);
    for (var key in attrs) {
        if (attrs.hasOwnProperty(key)) {
            ele.setAttribute(key, attrs[key]);
        }
    }
    return ele;
}

function reloadCommands() {
    CommandScript.remove();
    CommandsLoaded = false;
    
    Commands = undefined;
    UserCommands = undefined;
    ADMIN_COMMANDS = undefined;
    var TalosCommands = makeElement('script', {'type':'text/javascript',
                                           'src': URL + 'Commands.js',
                                           'onload':'CommandsLoaded = true',
                                           'id':'CommandScript'});
    document.head.appendChild(TalosCommands);
}

/*
    -------------------
    Main loop functions
    -------------------
*/

function writingHour() {
    d = new Date();

    if (d.getUTCHours() == (WH_TIME === 0 ? 23 : WH_TIME - 1)  && d.getUTCMinutes() == 50 && WHSwitch === 0) {
        postMessage("[b][Alert][/b] 10 minute mark!");
        WHSwitch++;
    } else if (d.getUTCHours() == (WH_TIME === 0 ? 23 : WH_TIME - 1) && d.getUTCMinutes() == 55 && WHSwitch == 1) {
        postMessage("[b][Alert][/b] 5 minute mark!");
        WHSwitch++;
    } else if (d.getUTCHours() == WH_TIME && d.getUTCMinutes() === 0 && WHSwitch == 2) {
        postMessage("[b]Productivity hour with Talos[/b] Time to do that thing you've been meaning to all day!");
        WHSwitch++;
    } else if (d.getUTCHours() == (WH_TIME == 23 ? 0 : WH_TIME + 1) && d.getUTCMinutes() === 0 && WHSwitch == 3) {
        setTimeout(function() {postMessage("[b]Productivity is over.[/b]");}, 500);
        WHSwitch = 0;
    }
}

function readChat() {
    if (!elementByID(messageContainer) && elementByID(messageTable).firstChild.innerHTML != "Previous messages parsed (press ESC to re-parse page)") { //First check is if we're on a page with normal chat table. Second is that that page is parsed.
        return;
    }
    var Messages = elementByID(messageTable).innerHTML.split("\n");
    for (var i = 1; i < Messages.length; i++) {
        var Message = Messages[i];
        if (Message.match(/<b .*>(.*)<\/b>: \^(\w+)(?:\s(.+))?(?:&nbsp;)/)) {
            
            var User = RegExp.$1;
            var Command = RegExp.$2;
            var Args = parseArgs(RegExp.$3);
            var isAdmin = false;
            for (var U in ADMINS) {
                if (User == ADMINS[U]) {
                    isAdmin = true;
                    break;
                }
            }
            
            if (window.ADMIN_COMMANDS[Command] && isAdmin) {
                log.warn("Admin command " + Command + " called by " + User);
                log.debug("With arguments \"" + Args + "\"");
                window.ADMIN_COMMANDS[Command](Args, User);
            } else if (IsSleeping == 1) {
                break;
            } else if (window.ADMIN_COMMANDS[Command] && !isAdmin) {
                log.warn("Admin command " + Command + " ignored from " + User);
                log.debug("With arguments \"" + Args + "\"");
                postMessage("Sorry, that command is Admin only, and I don't recognize you!");
            } else if (window.UserCommands[Command]){
                log.info("User command " + Command + " called by " + User);
                log.debug("With arguments \"" + Args + "\"");
                window.UserCommands[Command](Args, User);
            } else if (window.Commands[Command]) {
                log.info("Command " + Command + " called by " + User);
                log.debug("With arguments \"" + Args + "\"");
                window.Commands[Command](Args);
            } else {
                postMessage("Sorry, I don't understand that. May I suggest ^help?");
            }
        }
    }
    
    
    elementByID(messageTable).innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
    window[isCleared] = false;
}

function readPMs() {
    var ReceivedPM = elementByID(popup).innerHTML;
    var PMSearch = new RegExp('<!--' + PMTag + '-->.+>(.+)<\/em>.+' + textBox + '">\\^(\\w+)[\\W]?(?:\\s(.+))?(?:<\/div><p)');
    if (ReceivedPM.match(PMSearch)) {
        
        var User = RegExp.$1;
        var Command = RegExp.$2;
        var Args = parseArgs(RegExp.$3);
        var isAdmin = false;
        for (var U in ADMINS) {
            if (User == ADMINS[U]) {
                isAdmin = true;
                break;
            }
        }
        
        if (window.ADMIN_COMMANDS[Command] && isAdmin) {
            log.warn("Admin command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            window.ADMIN_COMMANDS[Command](Args);
        } else if (IsSleeping == 1) {
            closePopup();
            return;
        } else if (window.ADMIN_COMMANDS[Command] && !isAdmin) {
            log.warn("Admin command " + Command + " ignored from " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            privateMessage(User, "Sorry, that command is Admin only, and I don't recognize you!");
        } else if (window.UserCommands[Command]) {
            log.info("User command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            window.Commands[Command](Args, User);
        } else if (window.Commands[Command]) {
            log.info("Command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            window.Commands[Command](Args);
        } else {
            privateMessage(User, "Sorry, I don't understand that. May I suggest ^help?");
        }
    }
}

function mainLoop() {
    writingHour();
    if (CommandsLoaded) {
        readChat();
        readPMs();
    }
}

/*
    -------------------
    Initialization Code
    -------------------
*/

function loggerInit() {
    var Logger = makeElement('script', {'type':'text/javascript',
                                    'src': URL + 'log4javascript.js',
                                    'onload':'talosInit()'});
    document.head.appendChild(Logger);
}

function talosInit() {
    var TalosCommands = makeElement('script', {'type':'text/javascript',
                                           'src': URL + 'Commands.js',
                                           'onload':'CommandsLoaded = true',
                                           'id':'CommandScript'});
    document.head.appendChild(TalosCommands);
    
    var ChatzyAPI = makeElement('script', {'type':'text/javascript',
                                       'src': URL + 'ChatzyWrappers.js',
                                       'onload':'talosStart()'});
    document.head.appendChild(ChatzyAPI);
}

function talosStart() {
    log = log4javascript.getDefaultLogger();
    log.debug("Talos Booting");
    
    elementByID(messageTable).innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
    window[isCleared] = false;
    setInterval(function() {mainLoop();}, 1000);
    setInterval(function() {window[timeoutTimer] = new Date().getTime();}, 60000*10);
}

loggerInit();
