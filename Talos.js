/*
    ------------------
    Initialize Variables
    ------------------
*/

//Constants
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

/*
    User Commands dictionaries
*/
var Commands = {
	"seen": function(user) {
		//postMessage("Sorry, this command doesn't work yet.");
		if(user[0]) {
			var time;
			searchMessages("{V:" + user.join(" ") + "}");
			setTimeout(function() {
				var history = elementByID("X138").childNodes[2];
				if(history.childNodes[5]) {
					time = history.childNodes[5].innerText;
				} else {
					time = history.childNodes[4].innerText;
				}
			}, 300);
			setTimeout(function() {
				if(time) {
                    postMessage("User " + user.join(" ") + " was last seen " + time);
				} else {
					postMessage("I couldn't find that user. Sorry.");
				}
			}, 500);
			setTimeout(function() {
				X47();
			}, 750);
		} else {
			postMessage("Sorry, I need a user to look for.");
		}
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

function postMessage(message) {
    // X92.value = message;
    // X342();
    X279(message);
}

function closeChat() {
	postMessage("/close");
}

function openChat() {
	postMessage("/open");
}

function toggleChatLock() {
	if(X105.X398) { //Variable for whether the chat is locked, of course
		postMessage("/open");
	} else {
		postMessage("/close");
	}
}

function searchMessages(term) {
	postMessage("/find " + term);
}

function leaveChat() {
    elementByID("X802").onclick();
}

function privateMessage(name, message) {
	postMessage("/pm \"" + name + "\" " + message);
}

function globalMessage(message) { //Note, only sends the message to online users.
	var users = X330.split("\n");
	for (var i = 1; i <= users[0]; i++) {
		user = users[i].split("	");
		privateMessage(user[0], message);	//Replace the 0 with other numbers to grab different values. 2 is last leave/exit, 4 is status, 5 is location.
	}
}

//requires re-init of JSBot. Automate that?
function changeName(name) {
	X292('X387');

	setTimeout(function() {
		X481.value = name;
		X544.onsubmit();
	}, 1000);
}

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
    if (!elementByID("X971") && elementByID("X138").firstChild.innerHTML != "Previous messages parsed (press ESC to re-parse page)") {
        return;
    }
	var Messages = elementByID("X138").innerHTML.split("\n");
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
	
	
	elementByID("X138").innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
	X783 = false;
}

function readPMs() {
    var ReceivedPM = elementByID("X94").innerHTML;
    if (ReceivedPM.match(/<!--X268-->.+>(.+)<\/em>.+X296">\^(\w+)[\W]?(?:\s(.+))?(?:<\/div><p)/)) {
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
			X47();
			return;
		} else if (window["ADMIN_COMMANDS"][Command] && !isAdmin) {
		    privateMessage("Sorry, that command is Admin only, and I don't recognize you!");
		} else if (window["Commands"][Command]) {
			window["Commands"][Command](Args);
		} else {
		    privateMessage("Sorry, I don't understand that. May I suggest ^help?");
		}
    }
    //setTimeout(function(){ X47(); }, 100);
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
setInterval(function() {mainLoop();}, 1000);
setInterval(function() {postMessage("");}, 60000*10)
elementByID("X138").innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
X783 = false;
