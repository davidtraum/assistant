import time
import speech_recognition as sr
import json
import subprocess
from gtts import gTTS
import vlc
import sys

LANG = "de-DE";

DATA = dict();
PID = dict();
VARS = dict();
CONFIG = dict();
last_action = 0;

def getVar(name, defaut):
    if name in VARS:
        return VARS[name];
    else:
        return default;

with open('config.json') as file:
    CONFIG = json.loads(file.read());

commandfile = CONFIG['data-file'];
if len(sys.argv)>1:
    commandfile = sys.argv[1];
    
with open(commandfile) as file:
    DATA = json.loads(file.read());
    

def log(msg):
    print("[ASSISTANT] ", msg);
    
def say(msg, force=False):
    if(msg==None or not getVar('talk', False) and not force):
        return;
    result = gTTS(text=msg, lang=LANG[:2]);
    result.save("voice_out.mp3")
    player = vlc.MediaPlayer("voice_out.mp3");
    player.play();
    while str(player.get_state()) != 'State.Ended':
        print(player.get_state());
        time.sleep(0.1);

log("Language: " + LANG);

def process(text):
    global last_action;
    if(time.time() - last_action < 0.5):
        return;
    for key in DATA:
            entry = DATA[key];
            doExec = False;
            if('contains' in entry):
                for condition in entry['contains']:
                    full = True;
                    for word in condition:
                        if(not word in text):
                            full = False;
                            break;
                    if(full):
                        doExec = True;
                        break;
            if(doExec):
                execute(entry, text);
                last_action = time.time();
                return;
                
def execute(action, text):
    log("Executing " + action['name'] + "...");
    do = action['do'];
    msg = None;
    if('msg' in action):
        msg = action['msg'];
    if('append' in action):
        if(action['append']['mode'] == 'after'):
            parts = text.split(action['append']['content']);
            if(len(parts)>1):
                params = action['append']['content'].join(parts[1:])[1:]
                log("Parameters: " + params);
                do += params;
                if('to-msg' in action['append'] and action['append']['to-msg']):
                    msg+=params;
    if(action['type'] == 'cmd'):
        try:
            pid = subprocess.Popen(do.split(' '));
            log("Executed command: " + do);
            say(msg);
            if('pid' in action):
                if(action['pid']):
                    log("Saving Process");
                    if(action['pid-category'] in PID):
                        PID[action['pid-category']].append(pid);
                    else:
                        PID[action['pid-category']] = [pid];
        except Exception as e:
            print(e);
            log("An error occured while executing shell command.");
            if('error' in action):
                log("Running alternative...");
                execute(DATA[action['error']], text);
    elif(action['type'] == 'kill'):
        if action['do'] in PID:
            for proc in PID[do]:
                proc.terminate();
            del PID[action['do']];
            log("Processes terminated.");
        else:
            log("No process found");
    elif(action['type'] == 'query'):
        process(action['do']);
    elif(action['type'] == 'def'):
        for key in do:
            VARS[key] = do[key];
            log("Wert " + key + " auf " + str(do[key]) + " gesetzt.");
    
def callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="de-DE")
        text = text.lower();
        log("Understood: " + text);
        if(not CONFIG['keyword']['enabled'] or (CONFIG['keyword']['text'] in text)):
            if(CONFIG['sound']['confirm']):
                media = vlc.MediaPlayer("beep.mp3");
                media.play();
            process(text);
    except sr.UnknownValueError:
        pass;
    except sr.RequestError as e:
        log("Service error");
        log(e);

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)

log("Ready");
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_listening(wait_for_stop=False)
    log("Exit.");
    
