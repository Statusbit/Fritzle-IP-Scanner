'''
Name:       Fritzle-IP-Scanner.py
Ersteller:  Flo und Copilot
Version:    1.0 (06/2025)
Lizenz:     Keine (gerne diesen Kopf erhalten und erweitern)
Info:       Exportiert eine Geräteliste einer FritzBox 
Spende:     Ich trinke keinen Kaffee - Spende gerne an https://offroadkids.de/
            Off Road Kids Stiftung - Unterstützung für Straßenkinder und junge Obdachlose in Deutschland
'''
import subprocess
import sys
import pandas as pd
import os
import socket
import ctypes
import platform
import time
from fritzconnection.lib.fritzhosts import FritzHosts
from tqdm import tqdm
import getpass

# Logo
logo = """
    _/_/_/  _/_/_/          _/_/_/                                                              
     _/    _/    _/      _/          _/_/_/    _/_/_/  _/_/_/    _/_/_/      _/_/    _/  _/_/   
    _/    _/_/_/          _/_/    _/        _/    _/  _/    _/  _/    _/  _/_/_/_/  _/_/        
   _/    _/                  _/  _/        _/    _/  _/    _/  _/    _/  _/        _/           
_/_/_/  _/            _/_/_/      _/_/_/    _/_/_/  _/    _/  _/    _/    _/_/_/  _/            
"""

TITEL = "Fritzle-IP-Scanner"

def cls():
    os.system("cls" if platform.system() == "Windows" else "clear")

def set_window_title():
    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(TITEL)
        except:
            pass
        os.system(f'powershell -Command "[console]::Title = \'{TITEL}\'"')
    else:
        sys.stdout.write(f'\033]2;{TITEL}\a')

cls()
print(logo)
set_window_title()

print(f"╭───◉ Versuche die FritzBox automatisch zu ermitteln\n╰─⏱️ Gib mir kurz 'ne Sekunde")
time.sleep(3)

def get_fritzbox_ip():
    try:
        socket.setdefaulttimeout(2)
        return socket.gethostbyname("fritz.box")
    except socket.gaierror:
        return "192.168.178.1"

default_ip = get_fritzbox_ip()
print(f"\n╭───◉ Erkannte FritzBox-IP: {default_ip}")
manual_ip = input(f"├─🛜 Alternative IP-Adresse ( ↪️ = weiter ): ").strip()
FRITZBOX_IP = manual_ip if manual_ip else default_ip

USERNAME = input(f"├─🧑‍💼 Benutzername ( ↪️ = ohne ): ")
PASSWORD = getpass.getpass(f"╰─🗝️ Passwort der FritzBox: ")

print(f"\n╭───◉ Bitte warten – Verbindung wird hergestellt...\n├─⏳ Gib mir kurz noch 'n Augenblick")

try:
    fh = FritzHosts(address=FRITZBOX_IP, user=USERNAME, password=PASSWORD)
    devices = fh.get_hosts_info()
    print(f"╰─✅ Verbindung erfolgreich!")
except Exception as e:
    print(f"\n⚠ Anmeldung fehlgeschlagen! Fehler: {e}")
    input("\nDrücke die Eingabetaste, um es erneut zu versuchen...")
    sys.exit()

active_devices = sorted([device for device in devices if device["status"]], key=lambda x: x["ip"])

print(f"\n╭───◉ In welchem Format sollen die Daten gespeichert werden?")
print(f"├─ 1️- Textdatei")
print(f"├─ 2 - Excel-Datei")
print(f"├─ 3 - Beide Formate")
choice = input(f"╰─ Auswahl (1/2/3): ")

print(f"\n╭───◉ Daten werden verarbeitet...")

if choice in ["1", "3"]:
    with open("Fritzle_IP.txt", "w") as file:
        for i, device in enumerate(tqdm(active_devices, desc=f"├─💾 Speichern der Informationen")):
            file.write(f"{i}: IP: {device['ip']} | Name: {device['name']} | MAC: {device['mac']}\n")
    print(f"├─📄 Die Geräteliste wurde erfolgreich in 'Fritzle_IP.txt' gespeichert.")

if choice in ["2", "3"]:
    df = pd.DataFrame(active_devices)
    writer = pd.ExcelWriter("Fritzle_IP.xlsx", engine="xlsxwriter")
    df.to_excel(writer, sheet_name="FritzBox Geräte", index=False)

    worksheet = writer.sheets["FritzBox Geräte"]
    worksheet.set_column("A:C", 20)
    worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    writer.close()
    print(f"├─📑 Die Geräteliste wurde erfolgreich in 'Fritzle_IP.xlsx' gespeichert.")

input(f"╰─🏳️ Mit dem Ergebnis zufrieden? Ich trinke keinen Kaffee - Spende gerne an https://offroadkids.de/  ( ↪️ = beenden )")
