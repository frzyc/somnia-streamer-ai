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

## Run the bot
```
python main.py
```