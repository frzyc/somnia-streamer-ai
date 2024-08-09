# Somnia AI Stream bot
## A silly AI bot used to boost streamer/viewer interactions.
This is a python bot that uses ChatGPT and Azure Speech to do voice -> text -> chatGPT -> text -> voice.
There are also some OBS interactions to show visual interactions on stream.
Mainly used for https://www.twitch.tv/frzyc

# Running the bot
Steps to get the bot setup and running.
This project was created using python `3.11.0`
## Environmental variables
Copy and paste the `.env` file into `.env.local` file, and fill in the API keys and information in the new file.

## Create a virtual environment
Start a virtual environment
```
python -m venv .venv
```
## Install dependencies
You need to have `poetry` installed.
Use Poetry to enter the venv if not already in.
```
poetry shell
```

Use Poetry to install dependencies
```
poetry install
```

## Update Bot context
The [Bot context file](Somnia.txt) provides some context information for ChatGPT prompt, that should be personalized to each user.

## System structure
The system has been divided into 3 modules, so that modules are compartmentalized and can be hot-swapped at will. The modules will communicate using websockets, the ports are defined in the env files.
It is recommended to run Somnia first.

### Run Somnia
Somnia module listens to requests on the websocket, and generates response using ChatGPT. Will also connect to OBS to show specific image and update text, as well as TTS the response.
```
python somnia.py
```

### Run Voice-to-Text
This module allows users to speak to somnia, or type in a prompt. This will be sent to the Somnia module via Websockets.
```
python vtt.py
```

### Run Twitch bot
This module handles a lot of the Twitch stream interactions, listen to events, and dispatch prompts to Somnia via websocket.
```
python bot.py
```

### Run Twitch API
Because TwitchIO does not have a good ads API, this module is used to interface directly with twitch to detect when ads are running
```
python twitchApi.py
```

### Run stream pet
A pet that runs around on the bottom of the screen, the more chatters, the further it goes. Can give energy drink for mroe energy
```
python streampet.py
```