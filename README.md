# Talos
[![Build Status](https://travis-ci.org/CraftSpider/TalosBot.svg?branch=master)](https://travis-ci.org/CraftSpider/TalosBot)

A writing utility chatbot with releases for both Chatzy, an online chatroom service, and discord. Its mission? To have useful utility-type functions and others that can help writers.

The Chatzy release is JavaScript-based, and runs in a browser tab. The discord release is python, and requires the discord.py library.

## How to Run
If you wish to run this bot for yourself, here's how.  
  
### Chatzy
  First, a warning: Chatzy ToS states: "User scripts designed specifically to modify the behavior of Chatzy are not permitted."  
  Before you try running this bot yourself, make sure that you have received permission from Chatzy to do so on the room that you plan to run it in, as the devs of this bot are not responsible for any actions of Chatzy in response to your use.  
  
1. Open up a new Chatzy tab, and log into the room you wish to run in.
Make sure that timestamps are enabled in the room. The bot will not run without this setting being enabled. The setting can be changed by a room admin with the 'Room Properties' menu.

2. Open the console and paste in the code from the 'Chatzy\TalosStart.js' file. Hit 'enter'.
If prompted, allow popups- the window is the log4js console.

    - If you were prompted to allow popups, after doing so you may want to repeat step 2 so the log4js console actually opens.

3. Talos should now be running in that tab. Feel free to navigate away, try to avoid clicking on things on the page as it may confuse Talos.

### Discord
1. You will need to clone this repository onto your computer. You can do this through the command line with `git clone http://github.com/CraftSpider/TalosBot/`

2. Navigate into the discord\ file. Create a file named exactly `Token.txt` and place your discord bot token in that file.

3. Run the command `python3 Talos.py`. Talos should now be running.
