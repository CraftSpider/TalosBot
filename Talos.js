var NumWWs = 0;
var MaxWWs = 10;
var IsSleeping = 0;
const WH_TIME = 0;

var Admins = ["Dino", "α|CraftSpider|Ω", "HiddenStorys"];

var Commands = {
	"seen": function(user) {
	    postMessage("Sorry, this command doesn't work yet.");
// 		searchMessages("{V:" + user[0] + "}");
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
			    postMessage("Word War " + (length[1]? "'" + length[1] + "' " : "") + "ends. How did you do?");
			    NumWWs--;
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
		    for (var C in AdminCommands) {
		    	helpList += "^" + C + "\n"; 
		    }
		    postMessage(helpList);
	    } else {
	        switch (args[0]) {
	            case "help":
	                postMessage("Use: ^help [Command Name]\nDescription: Help command, by default gives general information about Talos and a list of available commands. Adding the name of another command as an argument will give a more detailed description of that command. Though you probably figured that out, you're here after all :P");
	                
	                break;
	            case "seen":
	                postMessage("Use: ^seen <Username>\nDescription:");
	                
	                break;
	            case "toggleLock":
	                postMessage("Use: ^toggleLock [time]\nDescription:");
	                
	                break;
	            case "wordWar":
	                postMessage("Use: ^wordWar <time> [keyword]\nDescription:");
	                
	                break;
	            default:
	        }
	    }
	}
};

var AdminCommands = {
    "toggleSleep": function() {
    	if (IsSleeping == 0) {
    		IsSleeping = 1;
    		postMessage("Good night! Going to sleep now. To wake me, type [b]^toggleSleep[/b] again.")
    	} else {
    		IsSleeping = 0;
    		postMessage("I'm awake again, and available for user commands. To have me sleep again, type [b]^toggleSleep[/b].")
    	}
	},
};

function postMessage(message) {
    // X92.value = message;
    // X342();
    X279(message);
}

function privateMessage(name, message) {
	postMessage("/pm \"" + name + "\" " + message);
}

//Note, only sends the message to online users.
function globalMessage(message) {
	var users = X330.split("\n");
	for (var i = 1; i <= users[0]; i++) {
		user = users[i].split("	");
		privateMessage(user[0], message);	//Replace the 0 with other numbers to grab different values. 2 is last leave/exit, 4 is status, 5 is location.
	}
}

function searchMessages(term) {
	postMessage("/find " + term);
	
}

///requires re-init of JSBot. Automate that?
function changeName(name) {
	X292('X387');

	setTimeout(function() {
		X481.value = name;
		X544.onsubmit();
	}, 1000);
}

function closeChat() {
	X279("/close");
}

function openChat() {
	X279("/open");
}

function toggleChatLock() {
	if(X105.X398) {
		X279("/open");
	} else {
		X279("/close");
	}
}

var WHActive = false;
var WHAlertOne = false;
var WHAlertTwo = false;

function writingHour() {
    d = new Date();
    
    if (d.getUTCHours() == WH_TIME && d.getUTCMinutes() == 0 && !WHActive) {
        postMessage("[b]Writing Hour has started.[/b] Have fun, and use it productively!");
        WHActive = true;
        setTimeout(function() {closeChat();}, 500);
        setTimeout(function() {
            openChat();
            setTimeout(function() {postMessage("[b]Writing Hour is over.[/b] How did you do?");}, 500);
            WHActive = false;
            WHAlertTwo = false;
            WHAlertOne = false;
        }, 60 * 60000);

    } else if (d.getUTCHours() == (WH_TIME == 0 ? 23 : WH_TIME - 1)  && d.getUTCMinutes() == 50 && !WHAlertOne) {
        postMessage("[b][Alert][/b] Writing Hour starts in 10 minutes!");
        WHAlertOne = true;

    } else if (d.getUTCHours() == (WH_TIME == 0 ? 23 : WH_TIME - 1) && d.getUTCMinutes() == 55 && !WHAlertTwo) {
        postMessage("[b][Alert][/b] Writing Hour starts in 5 minutes!");
        WHAlertTwo = true;
    }
}


function readChat() {
	var Messages = X17("X138").innerHTML.split("\n");
	for (var i = 1; i < Messages.length; i++) {
		var Message = Messages[i];
		if (Message.match(/<b .*>(.*)<\/b>: \^(\w+)(?:\s(.+))?/)) { //Instead of matching a set list of commands, match the word then check it against a dict?
		    var User = RegExp.$1;
			var Command = RegExp.$2;
			var Args = RegExp.$3.split(/[\s]|&nbsp;<span/);
		    var isAdmin = false;
			for (var U in Admins) {
			    if (User == Admins[U]) {
			        isAdmin = true;
			        break;
			    }
			}
			if (window["AdminCommands"][Command] && isAdmin) {
			    window["AdminCommands"][Command](Args);
			} else if (window["AdminCommands"][Command] && !isAdmin) {
			    postMessage("Sorry, that command is Admin only, and I don't recognize you!");
			} else if (window["Commands"][Command] && isSleeping == 0) {
				window["Commands"][Command](Args);
			} else {
			    postMessage("Sorry, I don't understand that. May I suggest ^help?");
			}
		}
	}
	
	
	X17("X138").innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
	X783 = false;
}

function mainLoop() {
    readChat();
    writingHour();
 
    
}

setInterval(function() {mainLoop();}, 1000);
X17("X138").innerHTML = '<P class="b">Previous messages hidden. (press ESC to re-parse page)</P>\n';
X783 = false;
