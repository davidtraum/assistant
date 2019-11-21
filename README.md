# Speech Assistant

## 1. About
This python program uses googles voice recognition to understand voice commands in the background. It can be used to start tasks,
search things on the internet and much more.
It can be used on your desktop pc, as well as on a raspberry pi or a comparable system. The requirements are only a microphone and internet connection.

## 2. Setup
After downloading the repository you need to install the python library dependencies. Those are:
- PyAudio
- SpeechRecognition
- gTTS
- vlc

## 3. Configuration
The general configuration is located in the config.json file.
To create your own commands, you must create a json file which is formatted like the example "commands.json" file.

## 4. Example Tasks and Commands

### Open the browser
This Configuration opens the browser by saying "start browser" or "open chrome"

        "chrome": {
            "name": "Start Chrome",
            "type": "cmd",
            "contains": [["open", "chrome"], ["start", "browser"]],
            "do": "google-chrome",
            "pid": true,
            "pid-category": "browser",
            "msg": "Started chrome browser"
            }
            
### Exit the browser
This Configuration kills all processes started by the voice recognition with category "browser"

        "exit-browser": {
            "name": "Quit Chrome",
            "type": "kill",
            "contains": [["exit", "chrome"], ["quit", "browser"]],
            "do": "browser",
            "msg": "Running browser sessions quit."
            },

