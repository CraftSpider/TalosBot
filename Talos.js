/*
    ------------------
    Initialize Variables
    ------------------
*/

//Constants
const VERSION = 1.5;
const BOOT_TIME = new Date();
const WH_TIME = 0; //What hour Writing Hour should start at, in UTC
const ADMIN_URL = "http://localhost:8000/Admins.txt"; //URL to pull admin list from
const ADMINS = []; //Will be filled with Admin data from file
const MAIN_URL = "https://rawgit.com/CraftSpider/TalosBot/master/"; //URL to load Commands from
const API_URL = "https://rawgit.com/CraftSpider/ChatzyAPI/master/"; //URL to load ChatzyAPI from

//Control variables
var CommandsLoaded = false;
var adminAliases = [];

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

function parseAdmins(str) {
    str = str.split(/\r?\n/);
    for (var i in str) {
        if (str.hasOwnProperty(i)) {
            str[i] = str[i].split(",")[1];
        }
    }
    return str;
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
    var oldItem = getStorage(key);
    window.localStorage.removeItem(key);
    return oldItem;
}

function makeElement(name, attrs) {
    var ele = document.createElement(name);
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
                                           'src': MAIN_URL + 'Commands.js',
                                           'onload':'CommandsLoaded = true',
                                           'id':'CommandScript'});
    document.head.appendChild(TalosCommands);
}

function readFile(file) {
    return new Promise(function(resolve, reject) {
        var rawFile = new XMLHttpRequest();
        rawFile.open("GET", file, false);
        rawFile.onreadystatechange = function () {
            if(rawFile.readyState === 4) {
                if(rawFile.status === 200 || rawFile.status === 0) {
                    var allText = rawFile.responseText;
                    resolve(allText);
                } else {
                    reject();
                }
            } else {
                reject();
            }
        };
        rawFile.send(null);
    });
}

function getAdminNames() {
    getVisitorData(["Alias","UID"]).then(function(visitorData) {
        adminAliases = [];
        for (var i = 0; i < visitorData.length; i++) {
            var visitor = visitorData[i];
            if (visitor[1] == "(Email hidden)") {
                continue;
            }
            if (visitor[1][0] == "\"") {
                visitor[1] =  visitor[1].substr(1,visitor[1].length-2);
            }
            for (var j = 0; j < ADMINS.length; j++) {
                if (ADMINS[j] == visitor[1]) {
                    adminAliases.push(visitor[0]);
                }
            }
        }
    });
}

/*
    -------------------
    Main loop functions
    -------------------
*/

function writingHour() {
    var d = new Date();

    if (d.getUTCHours() == (WH_TIME === 0 ? 23 : WH_TIME - 1)  && d.getUTCMinutes() == 50 && WHSwitch === 0) {
        postMessage("[b][Alert][/b] 10 minutes until WH!");
        WHSwitch++;
    } else if (d.getUTCHours() == (WH_TIME === 0 ? 23 : WH_TIME - 1) && d.getUTCMinutes() == 55 && WHSwitch == 1) {
        postMessage("[b][Alert][/b] 5 minutes until WH!");
        WHSwitch++;
    } else if (d.getUTCHours() == WH_TIME && d.getUTCMinutes() === 0 && WHSwitch == 2) {
        postMessage("[b]Writing Hour begins![/b] Time to write, good luck!");
        setTimeout(function(){closeChat();}, 1000);
        WHSwitch++;
    } else if (d.getUTCHours() == (WH_TIME == 23 ? 0 : WH_TIME + 1) && d.getUTCMinutes() === 0 && WHSwitch == 3) {
        setTimeout(function() {postMessage("[b]Writing Hour is over.[/b]");}, 500);
        setTimeout(function(){openChat();}, 1000);
        WHSwitch = 0;
    }
}

function readChat() {
    if (!elementByID(messageContainer) ||
            !elementByID(messageTable) ||
            !elementByID(messageTable).children ||
            elementByID(messageTable).firstChild.innerHTML != "Previous messages parsed (press ESC to re-parse page)") {
        return;
    }
    try {
        var Messages = elementByID(messageTable).children;
        for (var i = 1; i < Messages.length; i++) {
            try {
                var Message = Messages[i].childNodes;
                if(!Message[1] || !Message[1].data) {
                    continue;
                }
                
                var text = Message[1].data;
                
                if (text.match(/^: \^\w/)) {
                    var User = Message[0].innerText;
                    var Command = /\^(\w+)/.exec(text)[1];
                    var Args = text.substr(Command.length + 3).match(/([^\s"]+)|"(.+?)"/g);
                    
                    if (Args === null) {
                        Args = [];
                    }
                    
                    var isAdmin = false;
                    for (var U in adminAliases) {
                        if (User == adminAliases[U]) {
                            isAdmin = true;
                            break;
                        }
                    }
                    
                    //console.log(Command + " | " + /*FirstArgs + " |*/ "\"" + Args + "\"");
                    
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
                        log.debug("Failed to parse " + Command);
                        postMessage("Sorry, I don't understand that. May I suggest ^help?");
                    }
                }
            } catch (Exception) {}
        }
    } finally {
        elementByID(messageTable).innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
        window[isCleared] = false;
    }
}

function readPMs() {
    var ReceivedPM = elementByID(popup).innerHTML;
    var PMSearch = new RegExp('<!--' + PMTag + '-->.+>(.+)<\/em>.+' + textBox + '">\\^(\\w+)[\\W]?(?:\\s(.+))?(?:<\/div><p)');
    if (ReceivedPM.match(PMSearch)) {
        
        var User = RegExp.$1;
        var Command = RegExp.$2;
        var Args = parseArgs(RegExp.$3);
        var isAdmin = false;
        for (var U in adminAliases) {
            if (User == adminAliases[U]) {
                isAdmin = true;
                break;
            }
        }
        
        if (window.ADMIN_COMMANDS[Command] && isAdmin) {
            log.warn("Admin command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            window.ADMIN_COMMANDS[Command](Args);
        } else if (IsSleeping == 1 || (WHSwitch >= 3 && !isAdmin)) {
            closePopup();
            return;
        } else if (window.ADMIN_COMMANDS[Command] && !isAdmin) {
            log.warn("Admin command " + Command + " ignored from " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            privateMessage(User, "Sorry, that command is Admin only, and I don't recognize you!");
        } else if (window.UserCommands[Command]) {
            log.info("User command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            window.UserCommands[Command](Args, User);
        } else if (window.Commands[Command]) {
            log.info("Command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"");
            window.Commands[Command](Args);
        } else {
            log.debug("Failed to parse " + Command + " via PM");
            privateMessage(User, "Sorry, I don't understand that. May I suggest ^help?");
        }
    }
}

function mainLoop() {
    //writingHour();
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
                                    'src': MAIN_URL + 'log4javascript.js',
                                    'onload':'talosInit()'});
    document.head.appendChild(Logger);
}

function talosInit() {
    readFile(ADMIN_URL).then(function(fileText){
        parseAdmins(fileText).forEach(function(item) {ADMINS.push(item);});
        Object.freeze(ADMINS);
    });
    
    var TalosCommands = makeElement('script', {'type':'text/javascript',
                                           'src': MAIN_URL + 'Commands.js',
                                           'onload':'CommandsLoaded = true',
                                           'id':'CommandScript'});
    document.head.appendChild(TalosCommands);
    
    var ChatzyAPI = makeElement('script', {'type':'text/javascript',
                                       'src': API_URL + 'ChatzyWrappers.js',
                                       'onload':'talosStart()'});
    document.head.appendChild(ChatzyAPI);
}

function talosStart() {
    log = log4javascript.getDefaultLogger();
    localStorageAppender = new log4javascript.LocalStorageAppender();
    log.addAppender(localStorageAppender);
    
    log.debug("Talos Booting");
    
    getAdminNames();
    
    elementByID(messageTable).innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
    window[isCleared] = false;
    setInterval(function() {mainLoop();}, 1000);
    setInterval(function() {window[timeoutTimer] = new Date().getTime(); getAdminNames();}, 1000*60*10);
}

loggerInit();
