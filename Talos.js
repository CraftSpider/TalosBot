/*
    ------------------
    Initialize Variables
    ------------------
*/

//Constants
const VERSION = 1.1;
const BOOT_TIME = new Date();
const WH_TIME = 0;
const ADMINS = ["Dino", "α|CraftSpider|Ω", "HiddenStorys"];

//Command variables
var NumWWs = 0;
var MaxWWs = 10;
var IsSleeping = 0;

//Writing Hour variables
var WHActive = false;
var WHDisactive = false;
var WHAlertOne = false;
var WHAlertTwo = false;

//Writing Prompts words
var Nouns = ["dog", "cat", "robot", "astronaut", "man", "woman", "person", "child", "giant", "elephant", "zebra", "animal", "box", "tree", "wizard", "mage", "swordsman", "soldier", "inventor", "doctor", "Talos", "dinosaur", "insect", "nerd", "dancer", "singer", "actor", "barista", "acrobat", "gamer", "writer", "dragon"];
var Adjectives = ["happy", "sad", "athletic", "giant", "tiny", "smart", "silly", "unintelligent", "funny", "coffee-loving", "lazy", "spray-tanned", "angry", "disheveled", "annoying", "loud", "quiet", "shy", "extroverted", "jumpy", "ditzy", "strong", "weak", "smiley", "annoyed", "dextrous"];
var Goal = ["fly around the world", "go on a date", "win a race", "tell their crush how they feel", "find their soulmate", "write a chatbot", "get into university", "graduate high school", "plant a hundred trees", "find their biological parents", "fill their bucket list", "find atlantis", "learn magic", "learn to paint", "drive a car", "pilot a spaceship", "leave Earth", "go home", "redo elementary school", "not spill their beer"];
var Obstacle = ["learning to read", "fighting aliens", "saving the world", "doing algebra", "losing their hearing", "losing their sense of sight", "learning the language", "hacking the mainframe", "coming of age", "the nuclear apocalypse is happening", "incredibly drunk", "drinking coffee", "surfing", "spying on the bad guys", "smelling terrible", "having a bad hair day", "exploring the new planet", "on the moon", "on Mars"];


/*
    User Commands dictionaries
*/
var Commands = {
	"information": function() {
		postMessage("Hello! I'm Talos, official PtP mod-bot.\nMy Developers are CraftSpider, Dino, and HiddenStorys.\nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.");
	},
	"seen": function(user) {
		//postMessage("Sorry, this command doesn't work yet.");
		if(user[0]) {
			var time;
			searchMessages("{V:" + user.join(" ") + "}");
			setTimeout(function() {
				var recentMessage = messageTable.childNodes[2];
				if(recentMessage.childNodes[5]) {
					time = recentMessage.childNodes[5].innerText;
				} else {
					time = recentMessage.childNodes[4].innerText;
				}
			}, 500);
			setTimeout(function() {
				if(time) {
                    postMessage("User " + user.join(" ") + " was last seen " + time);
				} else {
					postMessage("I couldn't find that user. Sorry.");
				}
			}, 700);
			setTimeout(function() {
				closePopup();
			}, 900);
		} else {
			postMessage("Sorry, I need a user to look for.");
		}
	},
	"uptime": function() {
		postMessage("I've been online since " + BOOT_TIME.toUTCString() + ".");
	},
	"version": function() {
		postMessage("I'm currently on version " + VERSION);
	},
	"wordWar": function(length) {
		if (length[0] > 60 || length[0] <= 0) {
			postMessage("Choose a number between 1 and 60.");
		} else if (NumWWs >= MaxWWs) {
		    postMessage("Too many word wars, I can't keep up! Wait for one to finish first.");
		} else {
		    NumWWs++;
			postMessage("I'm starting a " + length[0] + " minute word war." + (length[1]? " Keyword: " + length[1]  + "." : "") + " Go!");
			setTimeout(function() {
				NumWWs--;
				if (!IsSleeping) {
					postMessage("Word War " + (length[1]? "'" + length[1] + "' " : "") + "ends. How did you do?");
				}
			}, length[0] * 60000);
		}
	},
	"prompt": function() {
		postMessage("A story about a " + Adjective[randomNumber(0, Adjective.length - 1);] + " " + Noun[randomNumber(0, Noun.length - 1);] + " who must " + Goal[randomNumber(0, Goal.length - 1);] + " while " + Obstacle[randomNumber(0, Goal.length - 1);] + ".");
	},
	"help": function (args) {
	    if (!args[0]) {
		    var helpList = "Greetings. I'm Talos, chat helper. My commands are:\n";
		    for (var C in Commands) {
		    	helpList += "^" + C + "\n"; 
		    }
		    helpList += "\nMy Admin Commands are:\n";
		    for (var C in ADMIN_COMMANDS) {
		    	helpList += "^" + C + "\n"; 
		    }
		    postMessage(helpList);
	    } else {
	        switch (args[0]) {
	            case "help":
	                postMessage("Use: ^help [Command Name]\nDescription: Help command, by default gives general information about Talos and a list of available commands. Adding the name of another command as an argument will give a more detailed description of that command. Though you probably figured that out, you're here after all :P");
	                
	                break;
	            case "kill":
	                postMessage("Use: ^kill\nDescription:");
	                break;
	            case "seen":
	                postMessage("Use: ^seen <Username>\nDescription: Find how long ago this user last posted a message. Currently doesn't work, sorry about that.");
	                
	                break;
	            case "toggleSleep":
	                postMessage("Use: ^toggleSleep [time]\nDescription: Turns user commands and related features off or on. An admin only command, to prevent abuse. Also doesn't declare the finish to any active WWs that finish while I'm asleep.");
	                
	                break;
	            case "wordWar":
	                postMessage("Use: ^wordWar <time> [keyword]\nDescription:");
	                
	                break;
	            default:
	                postMessage("Sorry, no available help page for that.");
	        }
	    }
	}
};

var ADMIN_COMMANDS = {
    "toggleSleep": function() {
    	if (IsSleeping == 0) {
    		IsSleeping = 1;
    		postMessage("Good night! Going to sleep now. To wake me, type [b]^toggleSleep[/b] again.");
    	} else {
    		IsSleeping = 0;
    		postMessage("I'm awake again, and available for user commands. To have me sleep again, type [b]^toggleSleep[/b].");
    	}
	},
	"kill": function() {
		postMessage("Et Tu, Brute?");
		setTimeout(function() {leaveChat();}, 200);
		throw new Error("Talos Killed by Admin");
	},
};

/*
    -----------------
    Wrapper Functions
    -----------------
*/
function elementByID(elementID) {
    return document.getElementById(elementID);
}

function closePopup() {
	X1774();
}

function postMessage(message) {
    X9646(message);
}

function closeChat() {
	postMessage("/close");
}

function openChat() {
	postMessage("/open");
}

function toggleChatLock() {
	if(X2667.X5476) { //Variable for whether the chat is locked, of course
		postMessage("/open");
	} else {
		postMessage("/close");
	}
}

function searchMessages(term) {
	postMessage("/find " + term);
}

function leaveChat() {
    elementByID("X2122").onclick();
}

function privateMessage(name, message) {
	postMessage("/pm \"" + name + "\" " + message);
}

function globalMessage(message) { //Note, only sends the message to online users.
	var users = X6958.split("\n");
	for (var i = 1; i <= users[0]; i++) {
		user = users[i].split("	");
		privateMessage(user[0], message);	//Replace the 0 with other numbers to grab different values. 2 is last leave/exit, 4 is status, 5 is location.
	}
}

//requires re-init of JSBot. Automate that?
function changeName(name) {
	X3132('X3221')

	setTimeout(function() {
		X2714.value = name;
		X6145.onsubmit();
	}, 1000);
}

/*
Arbitrary functions
*/

function randomNumber(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

/*

/*
    -------------------
    Main loop functions
    -------------------
*/
function writingHour() {
    d = new Date();
    
    if (d.getUTCHours() == (WH_TIME == 0 ? 23 : WH_TIME - 1)  && d.getUTCMinutes() == 50 && !WHAlertOne) {
        postMessage("[b][Alert][/b] Writing Hour starts in 10 minutes!");
        WHAlertOne = true;
    } else if (d.getUTCHours() == (WH_TIME == 0 ? 23 : WH_TIME - 1) && d.getUTCMinutes() == 55 && !WHAlertTwo) {
        postMessage("[b][Alert][/b] Writing Hour starts in 5 minutes!");
        WHAlertTwo = true;
    } else if (d.getUTCHours() == WH_TIME && d.getUTCMinutes() == 0 && !WHActive) {
        postMessage("[b]Writing Hour has started.[/b] Have fun, and use it productively!");
        WHActive = true;
        WHDisactive = false;
        setTimeout(function() {closeChat();}, 500);
    } else if (d.getUTCHours() == (WH_TIME == 23 ? 0 : WH_TIME + 1) && d.getUTCMinutes() == 0 && !WHDisactive) {
        openChat();
        setTimeout(function() {postMessage("[b]Writing Hour is over.[/b] How did you do?");}, 500);
        WHDisactive = true;
        WHActive = false;
        WHAlertTwo = false;
        WHAlertOne = false;
    }
}

function readChat() {
    if (!elementByID("X6285") && messageTable.firstChild.innerHTML != "Previous messages parsed (press ESC to re-parse page)") { //First check is if we're on a page with normal chat table. Second is that that page is parsed.
        return;
    }
	var Messages = messageTable.innerHTML.split("\n");
	for (var i = 1; i < Messages.length; i++) {
		var Message = Messages[i];
		if (Message.match(/<b .*>(.*)<\/b>: \^(\w+)(?:\s(.+))?(?:&nbsp;)/)) { //Instead of matching a set list of commands, match the word then check it against a dict?
		    var User = RegExp.$1;
			var Command = RegExp.$2;
			var Args = RegExp.$3.split(/\s/);
		    var isAdmin = false;
			for (var U in ADMINS) {
			    if (User == ADMINS[U]) {
			        isAdmin = true;
			        break;
			    }
			}
			if (window["ADMIN_COMMANDS"][Command] && isAdmin) {
			    window["ADMIN_COMMANDS"][Command](Args);
			} else if (IsSleeping == 1) {
				break;
			} else if (window["ADMIN_COMMANDS"][Command] && !isAdmin) {
			    postMessage("Sorry, that command is Admin only, and I don't recognize you!");
			} else if (window["Commands"][Command]) {
				window["Commands"][Command](Args);
			} else {
			    postMessage("Sorry, I don't understand that. May I suggest ^help?");
			}
		}
	}
	
	
	messageTable.innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
	X1281 = false;
}

function readPMs() {
    var ReceivedPM = elementByID("X8459").innerHTML;
    if (ReceivedPM.match(/<!--X4585-->.+>(.+)<\/em>.+X8195">\^(\w+)[\W]?(?:\s(.+))?(?:<\/div><p)/)) {
        var User = RegExp.$1;
        var Command = RegExp.$2;
		var Args = RegExp.$3.split(/\s/);
		var isAdmin = false;
		for (var U in ADMINS) {
		    if (User == ADMINS[U]) {
		        isAdmin = true;
		        break;
		    }
		}
		if (window["ADMIN_COMMANDS"][Command] && isAdmin) {
		    window["ADMIN_COMMANDS"][Command](Args);
		} else if (IsSleeping == 1) {
			closePopup();
			return;
		} else if (window["ADMIN_COMMANDS"][Command] && !isAdmin) {
		    privateMessage("Sorry, that command is Admin only, and I don't recognize you!");
		} else if (window["Commands"][Command]) {
			window["Commands"][Command](Args);
		} else {
		    privateMessage("Sorry, I don't understand that. May I suggest ^help?");
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
var messageTable = elementByID("X6817");
messageTable.innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
X1281 = false;
setInterval(function() {mainLoop();}, 1000);
setInterval(function() {postMessage("");}, 60000*10);
