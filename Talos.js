/*
    ------------------
    Initialize Variables
    ------------------
*/

//Constants
const VERSION = 1.4;
const BOOT_TIME = new Date();
const WH_TIME = 1;
const ADMINS = ["Dino", "α|CraftSpider|Ω", "HiddenStorys", "wundrweapon"];

//Command variables
var NumWWs = 0;
var MaxWWs = 10;
var IsSleeping = 0;
var getTime;

var loggedOn = {};

//Writing Hour variables
var WHSwitch = 0;

//Generator words
var Noun = ["dog", "cat", "robot", "astronaut", "man", "woman", "person", "child", "giant", "elephant", "zebra", "animal", "box", "tree", "wizard", "mage", "swordsman", "soldier", "inventor", "doctor", "Talos", "dinosaur", "insect", "nerd", "dancer", "singer", "actor", "barista", "acrobat", "gamer", "writer", "dragon"];
var Adjective = ["happy", "sad", "athletic", "giant", "tiny", "smart", "silly", "unintelligent", "funny", "coffee-loving", "lazy", "spray-tanned", "angry", "disheveled", "annoying", "loud", "quiet", "shy", "extroverted", "jumpy", "ditzy", "strong", "weak", "smiley", "annoyed", "dextrous"];
var Goal = ["fly around the world", "go on a date", "win a race", "tell their crush how they feel", "find their soulmate", "write a chatbot", "get into university", "graduate high school", "plant a hundred trees", "find their biological parents", "fill their bucket list", "find atlantis", "learn magic", "learn to paint", "drive a car", "pilot a spaceship", "leave Earth", "go home", "redo elementary school", "not spill their beer"];
var Obstacle = ["learning to read", "fighting aliens", "saving the world", "doing algebra", "losing their hearing", "losing their sense of sight", "learning the language", "hacking the mainframe", "coming of age", "the nuclear apocalypse is happening", "incredibly drunk", "drinking coffee", "surfing", "spying on the bad guys", "smelling terrible", "having a bad hair day", "exploring the new planet", "on the moon", "on Mars"];

var Place = ["pub", "spaceship", "museum", "office", "jungle", "forest", "coffee shop", "store", "market", "station", "tree", "hut", "house", "bed", "bus", "car", "dormitory", "school", "desert", "ballroom", "cattery", "shelter", "street"];
var Place_Adjective = ["quiet", "loud", "crowded", "deserted", "bookish", "colorful", "balloon-filled", "book", "tree", "money", "video game", "cat", "dog", "busy", "apocalypse", "writer", "magic", "light", "dark", "robotic", "futuristic", "old-timey"];
var Action = ["learn to read", "jump up and down", "cry a lot", "cry a little", "smile", "spin in a circle", "get arrested", "dance to the music", "listen to your favourite song", "eat all the food", "win the lottery", "hack the mainframe", "save the world", "find atlantis", "get accepted to Hogwarts", "swim around", "defy gravity", "spy on the bad guys", "drive a car", "enter the rocket ship", "learn math", "write a lot", "do gymnastics"];

/*
    --------------------------
    User Commands dictionaries
    --------------------------
*/

var Commands = {
    "credits": function() {
        postMessage("Primary Developers: CraftSpider, Dino.\nOther contributors: Wundrweapon, HiddenStorys")
    },
    "generate": function(type) {
        if (type[0].toUpperCase() == "PROMPT") {
            postMessage("A story about a " + Adjective[randomNumber(0, Adjective.length - 1)] + " " + Noun[randomNumber(0, Noun.length - 1)] + " who must " + Goal[randomNumber(0, Goal.length - 1)] + " while " + Obstacle[randomNumber(0, Goal.length - 1)] + ".");
        } else if (type[0].toUpperCase() == "CRAWL") {
            postMessage("You enter the " + Place_Adjective[randomNumber(0, Place_Adjective.length - 1)] + " " + Place[randomNumber(0, Place.length - 1)] + ". Write " + randomNumber(50, 500) + " words as you " + Action[randomNumber(0, Action.length - 1)] + ".");
        } else {
            postMessage("You can generate [b]prompt[/b]s and [b]crawl[/b] dares. Having trouble? Use ^help! :)");
        }
    },
    "information": function() {
        postMessage("Hello! I'm Talos, official PtP mod-bot.\nMy Developers are CraftSpider and Dino.\nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.");
    },
    "register": function(args) {
        if (args[0] && args[1]) {
            if (args[0].match(/[a-zA-Z]/) && args[1].match(/[a-zA-Z]/)) {
                TalosUser = {"password":args[1], "words":0};
                setStorage(args[0], stringify(TalosUser));
                postMessage("User " + args[0] + " has been registered!");
            } else {
                postMessage("Both username and password must contain at least one character, A-Z, case insensitive.");
            }
        } else {
            postMessage("I need both a username and a password to register an account.");
        }
    },
    "roulette": function() {
        var num = parseInt(Math.ceil(Math.random() * 12));
        switch(num) {
            case 0:
                postMessage("The chances of you getting this message are [i]vastly[/i] lower than that of any other. GG");
                break;
            case 1:
                postMessage("Save the game 10 times, just to be sure");
                break;
            case 2:
                postMessage("/me \u200B");
                break;
            case 3:
                postMessage("How much you wanna bet wundr broke Talos deliberately?");
                break;
            case 4:
                postMessage("This message has 50 characters in it\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B\u200B");
                break;
            case 5:
                postMessage("wundr's not good at making up dumb things for Talos to say, despite the fact that he himself speaks exclusively in stupid");
                break;
            case 6:
                var alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'];
                var arbitraryLetters = "";
                
                for (var i = 0; i < 10; i++) {
                    var index = parseInt(Math.floor(Math.random() * 26));
                    arbitraryLetters += alphabet[index];
                }
                
                postMessage("Arbitrary string of ten letters: " + arbitraryLetters);
                break;
            case 7:
                postMessage("Conglaturation, modified RNG pulled 7. Do not you are feel the luck?");
                break;
            case 8:
                postMessage("People don't think it be like it is, but it do");
                break;
            case 9:
                postMessage("/me crashes uncontrollably");
                break;
            case 10:
                postMessage("The only reason I have more than 7 statements is because wundr got bored of them #exposed");
                break;
            case 11:
                postMessage("/me makes a cryptic reference to SLeSbot");
                break;
            case 12:
                postMessage("woag 593 lines of code"); //intentional spelling error
                break;
            default:
                postMessage("pǝʞoɹq ɹ ᴉ | Go yell at " + ADMINS[3]);
        }
    },
    "seen": function(user) {
        if(user[0] && !getTime) {
            var time, iterations = 0;
            user = user.join(" ");
            searchMessages("", user);
            getTime = setInterval(function() {
                iterations++;
                if (elementsByClass(messageButton).length > 0) {
                    time = elementsByClass(messageTime)[0].innerText;
                    clearInterval(getTime);
                    getTime = undefined;
                    closePopup();
                    setTimeout(function() {
                        if (!IsSleeping) {
                            postMessage("User " + user + " was last seen " + time);
                        }
                    }, 500);
                } else if (iterations > 60 || elementByID(popup).childNodes[0].innerText == "No Messages Found") {
                    if (!IsSleeping) {
                        postMessage("I couldn't find " + user + ". Sorry.");
                    }
                    clearInterval(getTime);
                    getTime = undefined;
                    setTimeout(function() {
                        closePopup();
                    }, 500);
                }
            }, 500);
        } else if (user[0]) {
            postMessage("Previous seen command still running! Please wait between 10 seconds and a minute then ask again.");
        } else {
            postMessage("Sorry, I need a user to look for.");
            closePopup();
        }
    },
    "uptime": function() {
        var uptime = Math.floor((new Date() - BOOT_TIME)/1000);
        
        var weeks = Math.floor(uptime / 604800);
        uptime -= weeks * 604800;
        var days = Math.floor(uptime / 86400);
        uptime -= days * 86400;
        var hours = Math.floor(uptime / 3600);
        uptime -= hours * 3600;
        var minutes = Math.floor(uptime / 60);
        uptime -= minutes * 60;
        var seconds = Math.floor(uptime);
        
        var upStr = (weeks?weeks + " week" + (weeks == 1?"":"s") + ", ":"") +
                    (days?days + " day" + (days == 1?"":"s") + ", ":"") +
                    (hours?hours + " hour" + (hours == 1?"":"s") + ", ":"") +
                    (minutes?minutes + " minute" + (minutes == 1?"":"s") + ", and ":"") +
                    seconds + " second" + (seconds == 1?"":"s") + ".";
        
        postMessage("I've been online " + upStr);
    },
    "version": function() {
        postMessage("I'm currently on version " + VERSION);
    },
    "wordWar": function(args) {
        if (args[0] > 60 || args[0] <= 0) {
            postMessage("Choose a number between 1 and 60.");
        } else if (NumWWs >= MaxWWs) {
            postMessage("Too many word wars, I can't keep up! Wait for one to finish first.");
        } else {
            var length = args[0];
            var StartTime;
            var KeyWord;
            
            //Block of input handling. Checks for :xx format for times.
            if (args[1] && args[2]) {
                if (args[1].match(/:(\d\d)/)) {
                    StartTime = RegExp.$1;
                    KeyWord = args[2];
                } else if (args[2].match(/:(\d\d)/)) {
                    StartTime = RegExp.$1;
                    KeyWord = args[1];
                } else {
                    postMessage("I can't read that start time, sorry.");
                }
            } else if (args[1]) {
                if (args[1].match(/:(\d\d)/)) {
                    StartTime = RegExp.$1;
                } else {
                    KeyWord = args[1];
                }
            }
            
            //Yay for error handling.
            if (StartTime && (StartTime > 59 || StartTime < 0)) {
                postMessage("What part of the hour is that? Sorry, but I don't recognize that time.");
            } else {
                var TimeDif;
                NumWWs++;
                
                if (StartTime) {
                    //Figure out difference between StartTime and current time.
                    var CurTime = new Date();
                    var RawDif = StartTime - CurTime.getUTCMinutes();
                    RawDif = (RawDif >= 0 ? RawDif : RawDif + 60);
                    TimeDif = ((CurTime.getTime()-(CurTime.getSeconds()*1000+CurTime.getMilliseconds())) + RawDif * 60000) - CurTime.getTime();
                    postMessage("Alright, I'll start a " + length + " minute word war at :" + StartTime + "." + (KeyWord? " Keyword: " + KeyWord  + "." : ""));
                    // console.log(length + " " + StartTime + " " + TimeDif);
                    setTimeout(function() {
                        if (!IsSleeping) {
                            postMessage("[b]I'm starting the " + length + " minute word war." + (KeyWord? " Keyword: " + KeyWord  + "." : "") + " Go![/b]");
                        }
                        // console.log("I'm starting the " + length + " minute word war." + (KeyWord? " Keyword: " + KeyWord  + "." : "") + " Go!");
                        startWW(length, KeyWord);
                    }, TimeDif);
                } else {
                    postMessage("[b]I'm starting a " + length + " minute word war." + (KeyWord? " Keyword: " + KeyWord  + "." : "") + " Go![/b]");
                    startWW(length, KeyWord);
                }
            }
        }
    },
    "help": function(args) {
        if (!args[0]) {
            var helpList = "Greetings. I'm Talos, chat helper. My commands are:\n";
            for (var C in Commands) {
                if (C.toLowerCase() != "roulette") {
                    helpList += "^" + C + "\n";
                }
            }
            helpList += "My Admin Commands are:\n";
            for (C in ADMIN_COMMANDS) {
                if (ADMIN_COMMANDS.hasOwnProperty(C)) {
                    helpList += "^" + C + "\n";
                }
            }
            helpList += "See user commands list by typing '^help users'\n";
            postMessage(helpList);
        } else {
            switch (args[0]) {
                case "help":
                    postMessage("Use: ^help [Command Name]\nDescription: Help command, by default gives general information about Talos and a list of available commands. Adding the name of another command as an argument will give a more detailed description of that command. Though you probably figured that out, you're here after all :P");
                    break;
                case "generate":
                    postMessage("Use: ^generate <type>\nDescription: Generates a prompt. Currently available types are [b]prompt[/b] and [b]crawl[/b].");
                    break;
                case "information":
                    postMessage("Use: ^information\nDescription: Gives a short blurb about Talos.");
                    break;
                case "kill":
                    postMessage("Use: ^kill\nDescription: Causes Talos to immediately leave the chat, and cease running. Admin only.");
                    break;
                case "seen":
                    postMessage("Use: ^seen <Username>\nDescription: Find how long ago this user last posted a message. Returns a time or date in EST.");
                    break;
                case "toggleSleep":
                    postMessage("Use: ^toggleSleep [time]\nDescription: Turns user commands and related features off or on. An admin only command, to prevent abuse. Also doesn't declare the finish to any active WWs that finish while I'm asleep.");
                    break;
                case "uptime":
                    postMessage("Use: ^uptime\nDescription: Gives how long, down to the second, that Talos has been running.");
                    break;
                case "users":
                    var commandList = "User commands are:\n";
                    for (var UC in UserCommands) {
                        if (UserCommands.hasOwnProperty(UC)) {
                            commandList += "^" + UC + "\n";
                        }
                    }
                    postMessage(commandList);
                    break;
                case "version":
                    postMessage("Use: ^version\nDescription: The version that Talos is currently running. I always know exactly where I am.");
                    break;
                case "wordWar":
                    postMessage("Use: ^wordWar <length> [keyword] [start time]\nDescription: Starts a Word War, with given keyword and start time if provided. Start time should be two digits, the minute of the hour that the WW should start, and be prefixed by a colon. The length is in minutes, and Talos will say when that many minutes have elapsed.");
                    break;
                default:
                    postMessage("Sorry, no available help page for that.");
            }
        }
    }
};

var UserCommands = {
    "add": function(args, user) {
        if(loggedOn[user] && !isNaN(+args[1])) {
            args[1] = +args[1];
            TalosUser = parse(getStorage(loggedOn[user]));
            curVal = +TalosUser[args[0]];
            TalosUser[args[0]] = curVal + args[1];
            setStorage(loggedOn[user], stringify(TalosUser));
            postMessage(loggedOn[user] + " " + args[0] + " has been succesfully changed from " + curVal + " to " + (curVal + args[1]));
        } else if (loggedOn[user]) {
            postMessage("You can only add number inputs!");
        } else {
            postMessage("Sorry, you need to be logged on to do that");
        }
    },
    "check": function(args, user) {
        if (loggedOn[user]) {
            TalosUser = parse(getStorage(loggedOn[user]));
            if (TalosUser[args[0]] != "undefined" && TalosUser[args[0]] != "null") {
                curVal = TalosUser[args[0]];
                postMessage(loggedOn[user] + " " + args[0] + " is currently " + curVal);
            } else {
                postMessage("Your account doesn't have any value called " + args[0]);
            }
        } else {
            postMessage("Sorry, you need to be logged on to do that");
        }
    },
    "login": function(args, user) {
        if (!args[0] || !args[1]) {
            postMessage("I need both a username and a password!");
        } else if (!getStorage(args[0])) {
            postMessage("Sorry, I don't know any user named " + args[0]);
        } else {
            TalosUser = parse(getStorage(args[0]));
            if (args[1] == TalosUser.password && !loggedOn[user]) {
                loggedOn[user] = args[0];
                postMessage(user + " has been succesfully logged in!");
            } else if (args[1] == TalosUser.password) {
                postMessage("You appear to be already logged on as " + loggedOn[user]);
            } else {
                postMessage("That password doesn't match what I remember.");
            }
        }
    },
    "logout": function(args, user) {
        if (loggedOn[user]) {
            loggedOn[user] = undefined;
            postMessage(user + " has been logged out.");
        } else {
            postMessage("I can't log you out if you aren't even logged in.");
        }
    },
    "reset": function(args, user) {
        if (loggedOn[user] && args[0]) {
            TalosUser = parse(getStorage(loggedOn[user]));
            for (var key in TalosUser) {
                if (key == args[0]) {
                    TalosUser[key] = undefined;
                }
            }
            setStorage(loggedOn[user], stringify(TalosUser));
            postMessage(loggedOn[user] + " " + args[0] + " cleared.");
        } else if (loggedOn[user]) {
            postMessage("I need a value to reset!");
        } else {
            postMessage("Sorry, you need to be logged on to do that");
        }
    },
    "set": function(args, user) {
        if (loggedOn[user] && args[0]) {
            TalosUser = parse(getStorage(loggedOn[user]));
            TalosUser[args[0]] = args[1];
            setStorage(loggedOn[user], stringify(TalosUser));
            postMessage(loggedOn[user] + " " + args[0] + " has been set to " + args[1] + ".");
        } else if (loggedOn[user]) {
            postMessage("I can only set the value of Words to a number!");
        } else {
            postMessage("Sorry, you need to be logged on to do that");
        }
    },
    "subtract": function(args, user) {
        if(loggedOn[user] && !isNaN(+args[1])) {
            TalosUser = parse(getStorage(loggedOn[user]));
            curVal = TalosUser[args[0]];
            TalosUser[args[0]] -= +args[1];
            setStorage(loggedOn[user], stringify(TalosUser));
            postMessage(loggedOn[user] + " " + args[0] + " has been succesfully changed from " + curVal + " to " + (curVal - +args[1]));
        } else if (loggedOn[user]) {
            postMessage("You can only subtract number inputs!");
        } else {
            postMessage("Sorry, you need to be logged on to do that");
        }
    },
};

var ADMIN_COMMANDS = {
    "clearLogin": function() {
        loggedOn = {};
        postMessage("Logged in users cleared.");
    },
    "kill": function() {
        postMessage("Et Tu, Brute?");
        log.fatal("Talos killed on " + new Date());
        setInterval(function() {leaveChat();}, 200);
        window.open('http://www.chatzy.com/', '_self');
    },
    "listUsers": function() {
        out = "Current list of all users:\n";
        for (var key in window.localStorage) {
            if(isNaN(+getStorage(key))) {
                out += key + "\n";
            }
        }
        postMessage(out);
    },
    "removeUser": function(args) {
        if (args[0]) {
            for (var key in window.localStorage) {
                if (args[0] == key) {
                    removeStorage(key);
                    postMessage("User " + args[0] + " succesfully removed.");
                    return;
                }
            }
            postMessage("I couldn't find that user, sorry.");
        } else {
            postMessage("I need a username to search for!");
        }
    },
    "resetUser": function(args) {
        if (args[0]) {
            for (var key in window.localStorage) {
                if (args[0] == key) {
                    TalosUser = getStorage(key);
                    for (var value in TalosUser) {
                        if (value != "password") {
                            value = undefined;
                        }
                    }
                    postMessage("Succesfully reset user " + args[0]);
                    return;
                }
            }
            postMessage("I couldn't find that user, sorry.");
        } else {
            postMessage("I need a username to search for!");
        }
    },
    "toggleSleep": function(time) {
        if (IsSleeping === 0) {
            IsSleeping = 1;
            postMessage("Good night! Going to sleep " + (time[0]?"for " + time[0] + " minutes":"now") + ". To wake me, type [b]^toggleSleep[/b] again.");
        } else {
            IsSleeping = 0;
            postMessage("I'm awake again" + (time[0]? " for " + time[0] + " minutes":"") + ", and available for user commands. To have me sleep again, type [b]^toggleSleep[/b].");
        }
        if (time[0]) {
            setTimeout(function(){
                ADMIN_COMMANDS.toggleSleep("");
            }, time[0] * 60000);
        }
    },
};

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

/*
    -------------------
    Main loop functions
    -------------------
*/

function writingHour() {
    d = new Date();

    if (d.getUTCHours() == (WH_TIME === 0 ? 23 : WH_TIME - 1)  && d.getUTCMinutes() == 50 && WHSwitch === 0) {
        postMessage("[b][Alert][/b] 10 minutes until WH!");
        WHSwitch++;
    } else if (d.getUTCHours() == (WH_TIME === 0 ? 23 : WH_TIME - 1) && d.getUTCMinutes() == 55 && WHSwitch == 1) {
        postMessage("[b][Alert][/b] 5 minutes until WH!");
        WHSwitch++;
    } else if (d.getUTCHours() == WH_TIME && d.getUTCMinutes() === 0 && WHSwitch == 2) {
        postMessage("[b]Writing Hour begins![/b] Time to write, good luck!");
        setTimeout(function(){closeChat()}, 1000)
        WHSwitch++;
    } else if (d.getUTCHours() == (WH_TIME == 23 ? 0 : WH_TIME + 1) && d.getUTCMinutes() === 0 && WHSwitch == 3) {
        setTimeout(function() {postMessage("[b]Writing Hour is over.[/b]");}, 500);
        setTimeout(function(){openChat()}, 1000)
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
                log.debug("With arguments \"" + Args + "\"")
                window.ADMIN_COMMANDS[Command](Args, User);
            } else if (IsSleeping == 1) {
                break;
            } else if (window.ADMIN_COMMANDS[Command] && !isAdmin) {
                log.warn("Admin command " + Command + " ignored from " + User);
                log.debug("With arguments \"" + Args + "\"")
                postMessage("Sorry, that command is Admin only, and I don't recognize you!");
            } else if (window.UserCommands[Command]){
                log.info("User command " + Command + " called by " + User);
                log.debug("With arguments \"" + Args + "\"")
                window.UserCommands[Command](Args, User);
            } else if (window.Commands[Command]) {
                log.info("Command " + Command + " called by " + User);
                log.debug("With arguments \"" + Args + "\"")
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
            log.debug("With arguments \"" + Args + "\"")
            window.ADMIN_COMMANDS[Command](Args);
        } else if (IsSleeping == 1) {
            closePopup();
            return;
        } else if (window.ADMIN_COMMANDS[Command] && !isAdmin) {
            log.warn("Admin command " + Command + " ignored from " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"")
            privateMessage(User, "Sorry, that command is Admin only, and I don't recognize you!");
        } else if (window.UserCommands[Command]) {
            log.info("User command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"")
            window.Commands[Command](Args, User);
        } else if (window.Commands[Command]) {
            log.info("Command " + Command + " called by " + User + " via PM");
            log.debug("With arguments \"" + Args + "\"")
            window.Commands[Command](Args);
        } else {
            privateMessage(User, "Sorry, I don't understand that. May I suggest ^help?");
        }
    }
}

function mainLoop() {
    readChat();
    writingHour();
    readPMs();
}

/*
    -------------------
    Initialization Code
    -------------------
*/

function loggerInit() {
    Logger = document.createElement('script');
    Logger.setAttribute('type', 'text/javascript');
    Logger.setAttribute('src', 'https://rawgit.com/CraftSpider/TalosBot/master/log4javascript.js');
    Logger.setAttribute('onload', 'talosInit()');
    document.head.appendChild(Logger);
}

function talosInit() {
    ChatzyAPI = document.createElement('script');
    ChatzyAPI.setAttribute('type', 'text/javascript');
    ChatzyAPI.setAttribute('src', 'https://rawgit.com/CraftSpider/TalosBot/master/ChatzyWrappers.js');
    ChatzyAPI.setAttribute('onload', 'talosStart()');
    document.head.appendChild(ChatzyAPI);
}

function talosStart() {
    log = log4javascript.getDefaultLogger();
    log.debug("Talos Booting")
    
    elementByID(messageTable).innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
    window[isCleared] = false;
    setInterval(function() {mainLoop();}, 1000);
    setInterval(function() {window[timeoutTimer] = new Date().getTime();}, 60000*10);
}

loggerInit();
