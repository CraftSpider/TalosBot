/*
    --------------------
    Initialize Variables
    --------------------
*/

//Constants
const VERSION = 1.6; //Current Version. Increment upon major changes to structure or functionality.
const BOOT_TIME = new Date(); //Exact time of Talos boot, used to determine uptime.
const WH_TIME = 0; //What hour Writing Hour should start at, in UTC
const ADMIN_URL = "http://localhost:8000/Admins.txt"; //URL to pull admin list from
const ADMINS = []; //Will be filled with Admin data from file

//Control variables
var CommandsLoaded = false; //So that commands are not run while the Commands script is not yet loaded.
var adminAliases = []; //Current usernames of admins in chat. Will be filled by getAdminNames.

//Writing Hour variables
var WHSwitch = 0; //Used by WH function to determine what point it is at of its function.

/*
    -------------------
    Arbitrary functions
    -------------------
*/

/**
 * Returns a random number that is in the range of [min, max).
 * @param {int} min minimum value, inclusive
 * @param {int} max maximum value, exclusive
 * @returns {int} random number between those two values
 */
function randomNumber(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

/**
 * Starts a WW of the specified length with the specified keyword. WW ends itself after length has elapsed.
 * @param {float} length Length of the WW, in minutes
 * @param {String} keyword Keyword for the WW, a string that is used as an identifier for the start and end
 */
function startWW(length, KeyWord) {
    setTimeout(function() {
        NumWWs--;
        if (!IsSleeping) {
            postMessage("[b]Word War " + (KeyWord? "'" + KeyWord + "' " : "") + "ends.[/b] How did you do?");
        }
    }, length * 60000);
}

/**
 * Given the admin file as a string, converts it into a list of the admin's IDs. File is a CSV file in the form
 * <Nickname>,<User ID>
 * @param {String} str String form of the admin file.
 * @returns {Array} Chatzy Admin IDs
 */
function parseAdmins(str) {
    str = str.split(/\r?\n/);
    for (var i in str) {
        if (str.hasOwnProperty(i)) {
            str[i] = str[i].split(",")[1];
        }
    }
    return str;
}

/**
 * Parse a string of arguments into a list of strings. Split on spaces, except inside quotes.
 * @param {String} str String of arguments to parse
 * @returns {Array} Arguments as strings, quotations stripped
 */
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

/**
 * Simply a wrap for the JSON stringify function
 * @param {Object} object Object to turn into a String
 * @returns {String} string form of the object
 */
function stringify(object) {
    return JSON.stringify(object);
}

/**
 * A wrap for the JSON parse function
 * @param {String} string String to turn into an Object
 * @returns {Object} Object form of the input string
 */
function parse(string) {
    return JSON.parse(string);
}

/**
 * Sets the localStorage value for the given key and content
 * @param {String} key Key value within which to store the content
 * @param content Value to store in the key.
 */
function setStorage(key, content) {
    window.localStorage[key] = content;
}

/**
 * Returns the value of a specific key from the localStorage.
 * @param {String} key Key value to retrieve
 * @returns {String} Value of whatever was stored at that key location. undefined if nonextant.
 */
function getStorage(key) {
    return window.localStorage[key];
}

/**
 * Removes the specified key entirely from the localStorage
 * @param {String} key Key to remove from storage
 * @returns {String} Whatever was previously stored in localStorage.
 */
function removeStorage(key) {
    var oldItem = getStorage(key);
    window.localStorage.removeItem(key);
    return oldItem;
}

/**
 * Nulls out the Commands script variables, removes the script from the DOM, and reloads it.
 */
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

/**
 * Retrieves a file over HTTP, from a given URL or address.
 * @param {String} file Full URL link of file to retrieve.
 * @returns {Promise} A promise for the text of the file. Will resolve on succesfull retrieval, reject otherwise.
 */
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

/**
 * Empties out the adminAliases variable, then fills it with the current in-chat usernames of all admins.
 */
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

/**
 * Time based function that will run writing hour, at the hour specified by WH_TIME.
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

/**
 * Function that reads chat. Will parse chat as a list of HTML strings, and iterate through them.
 * Looks for commands of the form
 * ^<Command> <arg1> "<arg3>" ...
 * And passes those on to the ADMIN_COMMANDS, UserCommands, or Commands dict in that precedence.
 */
function readChat() {
    if ((!elementByID(messageContainer) ||
            !elementByID(messageTable) ||
            !elementByID(messageTable).children) &&
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

/**
 * Reads received PMs, using the same command format as used for read chat messsages.
 */
function readPMs() {
    var Popup = elementByID(popup);
    var PMSearch = new RegExp('<!--' + PMTag + '-->.+>(.+)<\/em>.+' + textBox + '">\\^(\\w+)[\\W]?(?:\\s(.+))?(?:<\/div><p)');
    if (Popup.innerHTML.match(PMSearch)) {
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
    } else if (Popup.style.display === "") {
        closePopup();
    }
}

/**
 * Primary running loop of Talos. This will be called once per second by default, and in turn should
 * call helper functions to perform actual operations.
 */
function mainLoop() {
    //writingHour();
    if (CommandsLoaded) {
        readChat();
        readPMs();
    }
}

/**
 * Starts Talos. Reads in admin file and turns it to names, sets up chat for readChat, and spins off the
 * mainLoop as well as a process to periodically reset the timeout and get the admin names again.
 */
function talosStart() {
    log.debug("Talos Starting");
    
    readFile(ADMIN_URL).then(function(fileText){
        parseAdmins(fileText).forEach(function(item) {ADMINS.push(item);});
        Object.freeze(ADMINS);
        getAdminNames();
    });
    
    elementByID(messageTable).innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
    window[isCleared] = false;
    setInterval(function() {mainLoop();}, 1000);
    setInterval(function() {window[timeoutTimer] = new Date().getTime(); getAdminNames();}, 1000*60*10);
}
