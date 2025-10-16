import threading
import base64
import os
import time
import re
import requests
import socket
import sys
from time import sleep
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
from collections import deque, defaultdict, Counter
import random
import hashlib
import platform
import subprocess
import string
import urllib.parse
import statistics
import math
import traceback

# Check và cài đặt các thư viện cần thiết
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    import pytz
    from faker import Faker
    from requests import session
    # Thư viện Rich cho giao diện xác thực key
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
except ImportError:
    print('__Đang cài đặt thư viện nâng cấp, vui lòng chờ...__')
    os.system("pip install requests colorama pytz faker rich")
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

# CONFIGURATION FOR VIP KEY
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display (từ keyv8.py)
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

# Đổi tên hàm banner của file banner.py để tránh xung đột
def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
████████╗██████╗░██╗░░██╗
╚══██╔══╝██╔══██╗██║░██╔╝
░░░██║░░░██║░░██║█████═╝░
░░░██║░░░██║░░██║██╔═██╗░
░░░██║░░░██████╔╝██║░╚██╗
░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝
══════════════════════════

Tool VTD 3QQ
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# DEVICE ID AND IP ADDRESS FUNCTIONS
def get_device_id():
    """Generates a stable device ID based on CPU information."""
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]

    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    """Gets the user's public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    """Displays the banner, IP address, and Device ID."""
    authentication_banner() # Gọi hàm banner đã đổi tên
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")


# FREE KEY HANDLING FUNCTIONS
def luu_thong_tin_ip(ip, key, expiration_date):
    """Saves free key information to a json file."""
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('ip_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    """Loads free key information from the json file."""
    try:
        with open('ip_key.json', 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def kiem_tra_ip(ip):
    """Checks for a saved free key for the current IP."""
    data = tai_thong_tin_ip()
    if data and ip in data:
        try:
            expiration_date = datetime.fromisoformat(data[ip]['expiration_date'])
            if expiration_date > datetime.now():
                return data[ip]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_key_and_url(ip_address):
    """Creates a free key and a URL to bypass the link."""
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'TDK{key1}{ip_numbers}'
    expiration_date = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    url = f'https://buffttfbinta.blogspot.com/2025/10/t.html?m={key}' # Link này có thể giữ nguyên hoặc thay đổi tùy admin
    return url, key, expiration_date

def get_shortened_link_phu(url):
    """Shortens the link to get the free key."""
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(ip_address):
    """Handles the entire process of obtaining a free key."""
    url, key, expiration_date = generate_key_and_url(ip_address)

    with ThreadPoolExecutor(max_workers=1) as executor:
        yeumoney_future = executor.submit(get_shortened_link_phu, url)
        yeumoney_data = yeumoney_future.result()

    if yeumoney_data and yeumoney_data.get('status') == "error":
        print(yeumoney_data.get('message'))
        return False

    link_key_yeumoney = yeumoney_data.get('shortenedUrl')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_yeumoney}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            sleep(2)
            luu_thong_tin_ip(ip_address, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_yeumoney}{trang}')


# VIP KEY HANDLING FUNCTIONS
def save_vip_key_info(device_id, key, expiration_date_str):
    """Saves VIP key information to a local cache file."""
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    """Loads VIP key information from the local cache file."""
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    """Calculates and displays the remaining time for a VIP key."""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()

        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    """Checks the VIP key from the URL on GitHub."""
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key (Status code: {response.status_code}).{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts

                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None

# MAIN AUTHENTICATION FLOW
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)
    key_info = {}

    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị cần thiết. Vui lòng kiểm tra kết nối mạng.{trang}")
        return False, None, None

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                key_info = {'type': 'VIP', 'key': cached_vip_info['key'], 'expiry': cached_vip_info['expiration_date']}
                sleep(3)
                return True, device_id, key_info
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key. Vui lòng nhập lại key.{trang}")

    if kiem_tra_ip(ip_address):
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn. Mời bạn dùng tool...{trang}")
        key_info = {'type': 'Free', 'key': 'Free Daily', 'expiry': datetime.now().strftime('%d/%m/%Y')}
        time.sleep(2)
        return True, device_id, key_info

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Dùng trong ngày){trang}")
        print(f"{trang}======================================")

        try:
            choice = input(f"{trang}[{do}<>{trang}] {xduong}Nhập lựa chọn của bạn: {trang}")
            print(f"{trang}═══════════════════════════════════")

            if choice == '1':
                vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP: {luc}')
                status, expiry_date_str = check_vip_key(device_id, vip_key_input)

                if status == 'valid':
                    print(f"{luc}Xác thực Key VIP thành công!{trang}")
                    save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                    display_remaining_time(expiry_date_str)
                    key_info = {'type': 'VIP', 'key': vip_key_input, 'expiry': expiry_date_str}
                    sleep(3)
                    return True, device_id, key_info
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else:
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                if process_free_key(ip_address):
                    key_info = {'type': 'Free', 'key': 'Free Daily', 'expiry': datetime.now().strftime('%d/%m/%Y')}
                    return True, device_id, key_info
                else:
                    return False, None, None

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except (KeyboardInterrupt):
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

NV={
    1:'Bậc thầy tấn công',
    2:'Quyền sắt',
    3:'Thợ lặn sâu',
    4:'Cơn lốc sân cỏ',
    5:'Hiếp sĩ phi nhanh',
    6:'Vua home run'
}

# Danh sách 10 bộ cược được chỉ định
BETTING_SETS = [
    [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6],
    [1, 3, 5], [2, 4, 6], [1, 3, 6], [2, 4, 5],
    [1, 2, 4], [2, 3, 5]
]

def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def prints(r, g, b, text="text", end="\n"):
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m", end=end)

def banner(game):
    banner="""
████████╗██████╗ ██╗  ██╗
 ╚══██╔══╝██╔══██╗██║ ██╔╝
    ██║   ██║  ██║█████╔╝
    ██║   ██║  ██║██╔═██╗
    ██║   ██████╔╝██║  ██╗
    ╚═╝   ╚═════╝ ╚═╝  ╚═╝
    """
    for i in banner.split('\n'):
        x,y,z=200,255,255
        for j in range(len(i)):
            prints(x,y,z,i[j],end='')
            x-=4
            time.sleep(0.001)
        print()
    prints(247, 255, 97,"✨" + "═" * 45 + "✨")
    prints(32, 230, 151,f"🌟 XWORLD - {game} ALQQV3 (QUANQUANV3) 🌟".center(45))
    prints(247, 255, 97,"═" * 47)
    prints(7, 205, 240,"Telegram: @tankeko12")
    prints(7, 205, 240,"Nhóm Zalo: https://zalo.me/g/ddxsyp497")
    prints(7, 205, 240,"Admin: DUONG PHUNG")
    prints(247, 255, 97,"═" * 47)

def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        prints(0, 255, 243,'Bạn có muốn sử dụng thông tin đã lưu hay không? (y/n): ',end='')
        x=input()
        if x.lower()=='y':
            with open('data-xw-cdtd.txt','r',encoding='utf-8') as f:
                return json.load(f)
        prints(247, 255, 97,"═" * 47)
    str_guide="""
    Hướng dẫn lấy link:
    1. Truy cập vào trang web xworld.io
    2. Đăng nhập tài khoản của bạn
    3. Tìm và nhấn vào "Chạy đua tốc độ"
    4. Nhấn "Lập tức truy cập"
    5. Copy link trang web đó và dán vào đây
"""
    prints(218, 255, 125,str_guide)
    prints(247, 255, 97,"═" * 47)
    prints(125, 255, 168,'📋 Nhập link của bạn:',end=' ')
    link=input()
    user_id=link.split('&')[0].split('?userId=')[1]
    user_secretkey=link.split('&')[1].split('secretKey=')[1]
    prints(218, 255, 125,f'    User ID của bạn là {user_id}')
    prints(218, 255, 125,f'    User Secret Key của bạn là {user_secretkey}')
    json_data={
        'user-id':user_id,
        'user-secret-key':user_secretkey,
    }
    with open('data-xw-cdtd.txt','w+',encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def get_betting_config(headers):
    if os.path.exists('config_cdtd_ctool.txt'):
        prints(0, 255, 243,'Phát hiện cấu hình đã lưu. Bạn có muốn sử dụng lại không? (y/n) ',end='')
        x=input()
        if x.lower()=='y':
            with open('config_cdtd_ctool.txt','r',encoding='utf-8') as f:
                return json.load(f)
    
    prints(247, 255, 97,"═" * 47)
    prints(0, 255, 243, 'Bạn muốn cài đặt cược thủ công hay để bot tự động cài đặt an toàn?\n (1: Thủ công / 2: Tự động): ', end='')
    setup_choice = input()
    prints(247, 255, 97,"═" * 47)
    
    str_coin_type="""
Nhập loại tiền mà bạn muốn chơi:
    1. USDT
    2. BUILD
    3. WORLD
"""
    prints(219, 237, 138,str_coin_type)
    while True:
        prints(125, 255, 168,'Nhập loại tiền bạn muốn chơi (1/2/3):',end=' ')
        x=input()
        if x in ['1', '2', '3']:
            Coin = {'1': 'USDT', '2': 'BUILD', '3': 'WORLD'}[x]
            break
        else:
            prints(247, 30, 30, 'Nhập sai, vui lòng nhập lại ...', end='\r')

    config = {}
    if setup_choice == '2':
        prints(255, 165, 0, 'BẠN ĐÃ CHỌN CHẾ ĐỘ CÀI ĐẶT CƯỢC AN TOÀN TỰ ĐỘNG')
        current_balance = user_asset(headers)[Coin]
        prints(0, 255, 19, f'Số dư {Coin} hiện tại của bạn là: {current_balance:.4f}')

        losses_to_withstand = 0
        while True:
            try:
                losses_to_withstand = int(input(f'    Bạn muốn tài khoản chịu được bao nhiêu tay thua liên tiếp? (ví dụ: 8): '))
                if losses_to_withstand > 0:
                    break
            except ValueError:
                prints(247, 30, 30, 'Vui lòng nhập một số nguyên hợp lệ.')

        use_multiplier = input('    Bạn có muốn gấp thếp (nhân tiền cược) sau khi thua không? (y/n): ').lower() == 'y'
        loss_multiplier = 1.0
        if use_multiplier:
            while True:
                try:
                    loss_multiplier = float(input('    Nhân bao nhiêu lần sau mỗi lần thua? (ví dụ: 2): '))
                    if loss_multiplier > 1.0:
                        break
                    else:
                        prints(247, 30, 30, 'Hệ số nhân phải lớn hơn 1.')
                except ValueError:
                    prints(247, 30, 30, 'Vui lòng nhập một số hợp lệ.')
        
        num_champions = 3 
        initial_coins = 0
        if loss_multiplier > 1.0:
            denominator = num_champions * (loss_multiplier**losses_to_withstand - 1)
            numerator = current_balance * (loss_multiplier - 1)
            if denominator > 0:
                initial_coins = numerator / denominator
        else:
            denominator = num_champions * losses_to_withstand
            if denominator > 0:
                initial_coins = current_balance / denominator

        initial_coins *= 0.95
        initial_coins = math.floor(initial_coins * 10000) / 10000.0

        if initial_coins <= 0:
            prints(247, 30, 30, 'Số dư không đủ để cài đặt tự động với số ván thua mong muốn. Vui lòng thử lại.')
            sys.exit()
            
        prints(0, 255, 19, f'    => Bot đã tính toán mức cược ban đầu an toàn cho MỖI NHÂN VẬT là: {initial_coins:.4f} {Coin}')
        coins = initial_coins

        take_profit = float(input(f'    Chốt lời khi đạt được bao nhiêu {Coin} (nhập 0 để bỏ qua): '))
        stop_loss = float(input(f'    Cắt lỗ khi thua bao nhiêu {Coin} (nhập 0 để bỏ qua): '))
        consecutive_loss_stop = losses_to_withstand + 1
        games_to_play = int(input('    Chơi bao nhiêu ván thì nghỉ (nhập 0 để chơi liên tục): '))
        games_to_rest = 0
        if games_to_play > 0:
            games_to_rest = int(input('    Nghỉ bao nhiêu ván rồi chơi tiếp: '))

        config = {
            'Coin': Coin, 'initial_coins': coins, 'current_coins': coins,
            'take_profit': take_profit if take_profit > 0 else 99999999,
            'stop_loss': stop_loss if stop_loss > 0 else 99999999,
            'consecutive_loss_stop': consecutive_loss_stop,
            'use_multiplier': use_multiplier, 'loss_multiplier': loss_multiplier,
            'games_to_play': games_to_play, 'games_to_rest': games_to_rest
        }

    else:
        prints(255, 13, 69,'BẠN ĐÃ CHỌN CHẾ ĐỘ CÀI ĐẶT CƯỢC THỦ CÔNG')
        coins = float(input(f'    Nhập số {Coin} bạn muốn đặt cho MỖI NHÂN VẬT: '))
        take_profit = float(input(f'    Chốt lời khi đạt được bao nhiêu {Coin} (nhập 0 để bỏ qua): '))
        stop_loss = float(input(f'    Cắt lỗ khi thua bao nhiêu {Coin} (nhập 0 để bỏ qua): '))
        consecutive_loss_stop = int(input('    Dừng tool sau bao nhiêu ván thua liên tiếp (nhập 0 để bỏ qua): '))
        
        prints(255, 165, 0, 'CÀI ĐẶT GẤP THẾP KHI THUA:')
        use_multiplier = input('    Bạn có muốn nhân tiền cược sau khi thua không? (y/n): ').lower() == 'y'
        loss_multiplier = 1.0
        if use_multiplier:
            loss_multiplier = float(input('    Nhân bao nhiêu lần sau mỗi lần thua? (ví dụ: 2): '))

        games_to_play = int(input('    Chơi bao nhiêu ván thì nghỉ (nhập 0 để chơi liên tục): '))
        games_to_rest = 0
        if games_to_play > 0:
            games_to_rest = int(input('    Nghỉ bao nhiêu ván rồi chơi tiếp: '))

        config = {
            'Coin': Coin, 'initial_coins': coins, 'current_coins': coins,
            'take_profit': take_profit if take_profit > 0 else 99999999,
            'stop_loss': stop_loss if stop_loss > 0 else 99999999,
            'consecutive_loss_stop': consecutive_loss_stop if consecutive_loss_stop > 0 else 99999999,
            'use_multiplier': use_multiplier, 'loss_multiplier': loss_multiplier,
            'games_to_play': games_to_play, 'games_to_rest': games_to_rest
        }

    with open('config_cdtd_ctool.txt','w+',encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return config

def top_100_cdtd():
    headers = {
        'accept': '*/*', 'accept-language': 'vi,en;q=0.9', 'origin': 'https://sprintrun.win',
        'priority': 'u=1, i', 'referer': 'https://sprintrun.win/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    }
    try:
        response = requests.get('https://api.sprintrun.win/sprint/recent_100_issues', headers=headers).json()
        nv = list(range(1, 7))
        kq = [response['data']['athlete_2_win_times'][str(i)] for i in nv]
        return nv, kq
    except Exception:
        prints(255, 0, 0, 'Lỗi: Không thể lấy dữ liệu 100 ván gần nhất. Đang thử lại...')
        time.sleep(5)
        return top_100_cdtd()

def top_10_cdtd(headers):
    try:
        response = requests.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers).json()
        ki = [i['issue_id'] for i in response['data']['recent_10']]
        kq = [i['result'][0] for i in response['data']['recent_10']]
        return ki, kq
    except Exception:
        prints(255, 0, 0, 'Lỗi: Không thể lấy dữ liệu 10 ván gần nhất. Đang thử lại...')
        time.sleep(5)
        return top_10_cdtd(headers)

def print_data(data_top10_cdtd, data_top100_cdtd):
    prints(247, 255, 97, "═" * 14 + " 10 VÁN GẦN NHẤT " + "═" * 13)
    for i in range(len(data_top10_cdtd[0])):
        r, g, b = [(255, 255, 0), (0, 255, 255), (255, 180, 220)][i % 3]
        text = f'  Kì {data_top10_cdtd[0][i]}: Người về nhất : {NV[int(data_top10_cdtd[1][i])]}'
        prints(r, g, b, text)
    
    prints(247, 255, 97, "═" * 13 + " 100 VÁN GẦN NHẤT " + "═" * 12)
    max_wins = max(data_top100_cdtd[1]) if data_top100_cdtd[1] else 1
    for i in range(6):
        wins = data_top100_cdtd[1][int(i)]
        bar_length = int((wins / max_wins) * 20)
        bar = "▇" * bar_length
        prints(255, 255, 0, f'  {NV[int(i+1)]:<16} về nhất {wins:<3} lần {bar}')
    prints(247, 255, 97, "═" * 47)

def select_betting_combination(data_top10_cdtd, data_top100_cdtd, game_count):
    """
    Chọn 1 trong 10 bộ 3 nhân vật để cược dựa trên phân tích dữ liệu.
    """
    try:
        last_winner = int(data_top10_cdtd[1][0])
        top_100_wins = {i + 1: count for i, count in enumerate(data_top100_cdtd[1])}
        sorted_by_wins = sorted(top_100_wins.items(), key=lambda item: item[1])
        
        min_wins = sorted_by_wins[0][1]
        least_frequent_champs = {champ for champ, wins in sorted_by_wins if wins == min_wins}

        max_wins = sorted_by_wins[-1][1]
        most_frequent_champs = {champ for champ, wins in sorted_by_wins if wins == max_wins}

        candidate_sets = [s for s in BETTING_SETS if last_winner not in s]
        if not candidate_sets:
            candidate_sets = BETTING_SETS

        cold_target_sets = [s for s in candidate_sets if any(champ in least_frequent_champs for champ in s)]
        if cold_target_sets:
            return cold_target_sets[game_count % len(cold_target_sets)]

        hot_target_sets = [s for s in candidate_sets if any(champ in most_frequent_champs for champ in s)]
        if hot_target_sets:
            return hot_target_sets[game_count % len(hot_target_sets)]
        
        if candidate_sets:
            return candidate_sets[game_count % len(candidate_sets)]
            
        return BETTING_SETS[game_count % len(BETTING_SETS)]
    except Exception:
        prints(255, 0, 0, "Lỗi trong quá trình phân tích, chọn cược theo mặc định.")
        return BETTING_SETS[game_count % len(BETTING_SETS)]

def kiem_tra_kq_cdtd(headers, kqs_dat, ki):
    prints(0, 255, 37, f'Đang đợi kết quả của kì #{ki}')
    start_time = time.time()
    while True:
        try:
            data_top10_cdtd = top_10_cdtd(headers)
            recent_issue_ids = [int(issue_id) for issue_id in data_top10_cdtd[0]]

            if int(ki) in recent_issue_ids:
                index = recent_issue_ids.index(int(ki))
                winner = int(data_top10_cdtd[1][index])
                
                prints(0, 255, 30,f'\nKết quả của kì {ki}: Người về nhất là {NV[winner]}')
                if winner in kqs_dat:
                    prints(0, 255, 37,'\n✨✨✨ XIN CHÚC MỪNG. BẠN ĐÃ THẮNG! ✨✨✨')
                    return True
                else:
                    prints(255, 0, 0,'\n💀💀💀 BẠN ĐÃ THUA. CHÚC BẠN MAY MẮN LẦN SAU! 💀💀💀')
                    return False
            
            elapsed_time = time.time() - start_time
            prints(0, 255, 197,f'Đang đợi kết quả {elapsed_time:.0f}s...', end='\r')
            time.sleep(1)
        except Exception:
            prints(255, 0, 0, "Lỗi: Không thể kiểm tra kết quả. Đang thử lại...")
            time.sleep(5)

def user_asset(headers):
    try:
        json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
        response = requests.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data).json()
        asset = {
            'USDT': response['data']['user_asset']['USDT'],
            'WORLD': response['data']['user_asset']['WORLD'],
            'BUILD': response['data']['user_asset']['BUILD']
        }
        return asset
    except Exception:
        prints(255, 0, 0, 'Lỗi: Không thể lấy thông tin số dư. Đang thử lại...')
        time.sleep(5)
        return user_asset(headers)

def print_stats_cdtd(stats, headers, config):
    try:
        current_asset = user_asset(headers)
        profit = current_asset[config['Coin']] - stats['asset_0']
        total_games = stats['win'] + stats['lose']
        win_rate = (stats['win'] / total_games * 100) if total_games > 0 else 0

        prints(247, 255, 97, "═" * 15 + "📊 THỐNG KÊ 📊" + "═" * 16)
        
        prints(70, 240, 234, f"  ✅ Thắng: {stats['win']}  |  ❌ Thua: {stats['lose']}  |  🎯 Tỉ lệ: {win_rate:.2f}%")
        prints(70, 240, 150, f"  ✨ Chuỗi thắng: {stats['consecutive_win']} (Max: {stats['max_consecutive_win']})")
        prints(255, 70, 70, f"  🔥 Chuỗi thua: {stats['consecutive_lose']} (Tối đa: {config['consecutive_loss_stop']})")
        
        loss_streak_counts = [f"{i}: {count}" for i, count in stats['loss_streaks'].items() if count > 0]
        if loss_streak_counts:
            prints(255, 120, 0, f"  💀 Lịch sử chuỗi thua: {', '.join(loss_streak_counts)}")

        if profit >= 0:
            prints(0, 255, 20, f"  💰 Lãi: +{profit:.4f} {config['Coin']}")
        else:
            prints(255, 0, 0, f"  💸 Lỗ: {profit:.4f} {config['Coin']}")
        
        prints(255, 165, 0, f"  🪙 Mức cược hiện tại: {config['current_coins']:.4f} {config['Coin']}")

        if config['games_to_play'] > 0:
            prints(100, 100, 255, f"  🎮 Ván trong phiên: {stats['games_played']}/{config['games_to_play']}")
            if stats['games_to_skip'] > 0:
                prints(255, 255, 0, f"  😴 Đang nghỉ, còn lại {stats['games_to_skip']} ván.")
        prints(247, 255, 97, "═" * 47)
    except Exception as e:
        prints(255, 0, 0, f'Lỗi: Không thể hiển thị thống kê. {e}')


def print_wallet(asset):
    prints(247, 255, 97,"═" * 47)
    prints(238, 250, 7,'SỐ DƯ CỦA BẠN:')
    prints(23, 232, 159,f" USDT:{asset['USDT']:.4f}    WORLD:{asset['WORLD']:.4f}    BUILD:{asset['BUILD']:.4f}".center(50))
    prints(247, 255, 97,"═" * 47)

def bet_cdtd(headers, ki, config, selected_champions):
    prints(0, 246, 255, f"💠 Bắt đầu đặt cược cho Kì #{ki} 💠")
    for champion_id in selected_champions:
        try:
            json_data = {
                'issue_id': int(ki), 'bet_group': 'winner', 'asset_type': config['Coin'],
                'athlete_id': champion_id, 'bet_amount': config['current_coins'],
            }
            response = requests.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data).json()
            if response.get('code') == 0 and response.get('msg') == 'ok':
                prints(0, 255, 19, f"    -> Đã đặt {config['current_coins']:.4f} {config['Coin']} cho '{NV[champion_id]}' thành công.")
            else:
                prints(255, 0, 0, f"    -> Đặt cược cho '{NV[champion_id]}' thất bại: {response.get('msg')}")
        except Exception:
            prints(255, 0, 0, f"    -> Lỗi nghiêm trọng khi đặt cược cho '{NV[champion_id]}'.")
        time.sleep(0.5)

def main_cdtd():
    banner("CHẠY ĐUA TỐC ĐỘ")
    data = load_data_cdtd()

    headers = {
        'accept': '*/*', 'accept-language': 'vi,en;q=0.9', 'cache-control': 'no-cache',
        'country-code': 'vn', 'origin': 'https://xworld.info', 'pragma': 'no-cache',
        'priority': 'u=1, i', 'referer': 'https://xworld.info/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'user-id': data['user-id'], 'user-login': 'login_v2',
        'user-secret-key': data['user-secret-key'], 'xb-language': 'vi-VN',
    }
    
    config = get_betting_config(headers)
    initial_asset = user_asset(headers)
    stats = {
        'win': 0, 'lose': 0, 
        'consecutive_lose': 0,
        'consecutive_win': 0,
        'max_consecutive_win': 0,
        'loss_streaks': {i: 0 for i in range(1, 10)},
        'asset_0': initial_asset[config['Coin']],
        'games_played': 0, 'games_to_skip': 0,
    }
    
    while True:
        clear_screen()
        banner('CHẠY ĐUA TỐC ĐỘ')
        current_asset = user_asset(headers)
        print_wallet(current_asset)
        
        data_top10_cdtd = top_10_cdtd(headers)
        data_top100_cdtd = top_100_cdtd()
        print_data(data_top10_cdtd, data_top100_cdtd)
        print_stats_cdtd(stats, headers, config)

        profit = current_asset[config['Coin']] - stats['asset_0']
        if profit >= config['take_profit']:
            prints(0, 255, 0, f"Đã đạt mục tiêu chốt lời! Dừng tool. Lãi: {profit:.4f} {config['Coin']}")
            break
        if -profit >= config['stop_loss']:
            prints(255, 0, 0, f"Đã chạm ngưỡng cắt lỗ! Dừng tool. Lỗ: {profit:.4f} {config['Coin']}")
            break
        if stats['consecutive_lose'] >= config['consecutive_loss_stop'] and config['consecutive_loss_stop'] > 0:
            prints(255, 0, 0, f"Đã thua {stats['consecutive_lose']} ván liên tiếp! Dừng tool.")
            break

        if stats['games_to_skip'] > 0:
            prints(255, 255, 0, f"Ván này nghỉ, bỏ qua đặt cược. Còn lại {stats['games_to_skip']} ván nghỉ.")
            stats['games_to_skip'] -= 1
            next_issue = data_top10_cdtd[0][0] + 1
            prints(100, 100, 255, f"Đang chờ qua kì #{next_issue}...")
            while True:
                try:
                    latest_issue = top_10_cdtd(headers)[0][0]
                    if latest_issue >= next_issue:
                        prints(0, 255, 0, f"Kì #{next_issue} đã kết thúc. Chuẩn bị cho ván tiếp theo.")
                        break
                except Exception:
                    pass
                time.sleep(5)
            time.sleep(10)
            continue
            
        game_count = stats['win'] + stats['lose']
        kqs_dat = select_betting_combination(data_top10_cdtd, data_top100_cdtd, game_count)

        prints(247, 255, 97, "═" * 10 + "🔮 PHÂN TÍCH & CHỌN CƯỢC 🔮" + "═" * 9)
        prints(0, 246, 255, f'  BOT CHỌN ĐẶT QUÁN QUÂN: {", ".join([NV[kq] for kq in kqs_dat])}')
        prints(247, 255, 97, "═" * 47)
        
        next_ki = data_top10_cdtd[0][0] + 1
        bet_cdtd(headers, next_ki, config, kqs_dat)
        
        result = kiem_tra_kq_cdtd(headers, kqs_dat, next_ki)
        
        if result:
            if stats['consecutive_lose'] > 0:
                streak_len = stats['consecutive_lose']
                if 1 <= streak_len <= 9:
                    stats['loss_streaks'][streak_len] += 1
            stats['win'] += 1
            stats['consecutive_win'] += 1
            if stats['consecutive_win'] > stats['max_consecutive_win']:
                stats['max_consecutive_win'] = stats['consecutive_win']
            stats['consecutive_lose'] = 0
            config['current_coins'] = config['initial_coins']
        else:
            stats['lose'] += 1
            stats['consecutive_lose'] += 1
            stats['consecutive_win'] = 0
            if config['use_multiplier']:
                config['current_coins'] *= config['loss_multiplier']
        
        stats['games_played'] += 1

        if config['games_to_play'] > 0 and stats['games_played'] >= config['games_to_play']:
            prints(255, 165, 0, f"Đã chơi {stats['games_played']} ván. Bắt đầu nghỉ {config['games_to_rest']} ván.")
            stats['games_to_skip'] = config['games_to_rest']
            stats['games_played'] = 0
        
        time.sleep(10)

# =====================================================================================
# PHẦN 3: LOGIC CHẠY CHÍNH
# =====================================================================================

if __name__ == "__main__":
    # Bước 1: Chạy xác thực key
    is_authenticated, device_id, key_info = main_authentication()

    # Bước 2: Nếu xác thực thành công, chạy tool chính
    if is_authenticated:
        print(f"\n{luc}Xác thực thành công. Bắt đầu chạy tool...{trang}")
        time.sleep(2)
        try:
            main_cdtd()
        except KeyboardInterrupt:
            prints(255, 0, 0, "\nĐã dừng tool theo yêu cầu của người dùng.")
        except Exception as e:
            traceback.print_exc()
            prints(255, 0, 0, f"\nĐã xảy ra lỗi không mong muốn: {e}. Tool sẽ tự động thoát.")
            input("Nhấn Enter để thoát...")
    else:
        print(f"\n{do}Xác thực không thành công. Tool sẽ thoát.{trang}")
        sys.exit()