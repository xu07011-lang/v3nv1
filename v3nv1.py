import base64
import hashlib
import json
import os
import platform
import random
import re
import string
import subprocess
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep

# Check and install necessary libraries
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    import pytz
    import requests
    import math # Thêm thư viện math cho v3nv1.py
    import traceback # Thêm thư viện traceback cho v3nv1.py
except ImportError:
    print('__Đang cài đặt các thư viện cần thiết, vui lòng chờ...__')
    # Use sys.executable to ensure pip corresponds to the current python environment
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "colorama", "pytz"])
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

# CONFIGURATION
FREE_CACHE_FILE = 'free_key_cache.json'      # Cache file for free key
VIP_CACHE_FILE = 'TDKf1.json'            # Cache file for VIP key
HANOI_TZ = pytz.timezone('Asia/Ho_Chi_Minh') # Hanoi timezone
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/keyxworkdf/main/keyxworkdf.txt" # URL containing the list of VIP keys

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

# Authentication banner
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
Admin: DUONG phung
Tool xworld VTD 3QQ
══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.0001)

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
    authentication_banner()
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")

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
        
def seeded_shuffle_js_equivalent(array, seed):
    seed_value = 0
    for i, char in enumerate(seed):
        seed_value = (seed_value + ord(char) * (i + 1)) % 1_000_000_000
    def custom_random():
        nonlocal seed_value
        seed_value = (seed_value * 9301 + 49297) % 233280
        return seed_value / 233280.0
    shuffled_array = array[:]
    current_index = len(shuffled_array)
    while current_index != 0:
        random_index = int(custom_random() * current_index)
        current_index -= 1
        shuffled_array[current_index], shuffled_array[random_index] = shuffled_array[random_index], shuffled_array[current_index]
    return shuffled_array

def save_free_key_info(device_id, key, expiration_date):
    """Saves free key information to a json file based on device_id."""
    data = {device_id: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(FREE_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)

def load_free_key_info():
    """Loads free key information from the json file."""
    try:
        with open(FREE_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def check_saved_free_key(device_id):
    """Checks for a saved free key for the current device_id."""
    data = load_free_key_info()
    if data and device_id in data:
        try:
            expiration_date = datetime.fromisoformat(data[device_id]['expiration_date'])
            if expiration_date > datetime.now(HANOI_TZ):
                return data[device_id]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_free_key_and_url(device_id):
    """Creates a free key based on device_id and a URL to bypass the link."""
    today_str = datetime.now(HANOI_TZ).strftime('%Y-%m-%d')
    seed_str = f"TDK_FREE_KEY_{device_id}_{today_str}"
    hashed_seed = hashlib.sha256(seed_str.encode()).hexdigest()
    digits = [d for d in hashed_seed if d.isdigit()][:10]
    letters = [l for l in hashed_seed if 'a' <= l <= 'f'][:5]
    while len(digits) < 10:
        digits.extend(random.choices(string.digits))
    while len(letters) < 5:
        letters.extend(random.choices(string.ascii_lowercase))
    key_list = digits + letters
    shuffled_list = seeded_shuffle_js_equivalent(key_list, hashed_seed)
    key = "".join(shuffled_list)
    now_hanoi = datetime.now(HANOI_TZ)
    expiration_date = now_hanoi.replace(hour=21, minute=0, second=0, microsecond=0)
    url = f'https://tdkbumxkey.blogspot.com/2025/10/lay-link.html?m={key}'
    return url, key, expiration_date

def get_shortened_link_phu(url):
    """Shortens the link to get the free key."""
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={urllib.parse.quote(url)}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": f"Lỗi {response.status_code}: Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(device_id):
    """Handles the entire process of obtaining a free key based on device_id."""
    if datetime.now(HANOI_TZ).hour >= 21:
        print(f"{do}Đã qua 21:00 giờ Việt Nam, key miễn phí cho hôm nay đã hết hạn.{trang}")
        print(f"{vang}Vui lòng quay lại vào ngày mai để nhận key mới.{trang}")
        time.sleep(3)
        return False

    url, key, expiration_date = generate_free_key_and_url(device_id)
    shortened_data = get_shortened_link_phu(url)

    if shortened_data and shortened_data.get('status') == "error":
        print(f"{do}{shortened_data.get('message')}{trang}")
        return False

    link_key_shortened = shortened_data.get('shortenedUrl')
    if not link_key_shortened:
        print(f"{do}Không thể tạo link rút gọn. Vui lòng thử lại.{trang}")
        return False

    print(f'{trang}[{do}<>{trang}] {hong}Vui Lòng Vượt Link Để Lấy Key Free (Hết hạn 21:00 hàng ngày).{trang}')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_shortened}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            if datetime.now(HANOI_TZ) >= expiration_date:
                print(f"{do}Rất tiếc, key này đã hết hạn vào lúc 21:00. Vui lòng quay lại vào ngày mai.{trang}")
                return False
            time.sleep(2)
            save_free_key_info(device_id, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_shortened}{trang}')

def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)

    if not device_id:
        print(f"{do}Không thể lấy thông tin Mã Máy. Vui lòng kiểm tra lại thiết bị.{trang}")
        return False, None, None # Thêm trả về None cho device_id và key_info

    # 1. Prioritize checking for a saved VIP key
    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                sleep(3)
                # Trả về True và thông tin key/device_id nếu xác thực thành công
                return True, device_id, {'type': 'vip', 'key': cached_vip_info['key']}
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key VIP. Vui lòng nhập lại key.{trang}")

    # 2. If no VIP key, check for a saved free key for the day
    if check_saved_free_key(device_id):
        expiry_str = f"21:00 ngày {datetime.now(HANOI_TZ).strftime('%d/%m/%Y')}"
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn (Hết hạn lúc {expiry_str}). Mời bạn dùng tool...{trang}")
        time.sleep(2)
        # Trả về True và thông tin key/device_id nếu xác thực thành công
        return True, device_id, {'type': 'free', 'key': check_saved_free_key(device_id)}

    # 3. If no key is saved, display the selection menu
    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Hết hạn 21:00 hàng ngày){trang}")
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
                    sleep(3)
                    # Trả về True và thông tin key/device_id
                    return True, device_id, {'type': 'vip', 'key': vip_key_input}
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else: # status == 'error'
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                if process_free_key(device_id):
                    # Lấy lại free key vừa lưu để trả về
                    saved_key = check_saved_free_key(device_id) 
                    return True, device_id, {'type': 'free', 'key': saved_key}
                # Nếu process_free_key trả về False, tiếp tục vòng lặp

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except KeyboardInterrupt:
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()
            
    return False, None, None

NV={
    1:'Bậc thầy tấn công',
    2:'Quyền sắt',
    3:'Thợ lặn sâu',
    4:'Cơn lốc sân cỏ',
    5:'Hiếp sĩ phi nhanh',
    6:'Vua home run'
}

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
    # Xử lý trường hợp link có dấu & ở cuối hoặc cấu trúc khác
    try:
        user_id_part = link.split('?userId=')[1].split('&')[0]
        user_secretkey_part = link.split('secretKey=')[1].split('&')[0]
        user_id = user_id_part
        user_secretkey = user_secretkey_part
    except IndexError:
        prints(255, 0, 0, 'Lỗi: Link không đúng định dạng. Vui lòng kiểm tra lại.')
        sys.exit()

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
                else:
                    prints(247, 30, 30, 'Số ván thua liên tiếp phải lớn hơn 0.')
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
            # S = a * (1 + r + r^2 + ... + r^(n-1)) = a * (r^n - 1) / (r - 1)
            denominator = num_champions * (loss_multiplier**losses_to_withstand - 1)
            numerator = current_balance * (loss_multiplier - 1)
            if denominator > 0:
                initial_coins = numerator / denominator
        else: # loss_multiplier = 1.0 (Không gấp thếp)
            # Tổng cược sau n ván thua: n * 3 * initial_coins
            # initial_coins = current_balance / (n * 3)
            denominator = num_champions * losses_to_withstand
            if denominator > 0:
                initial_coins = current_balance / denominator

        initial_coins *= 0.95
        # Làm tròn xuống 4 chữ số thập phân
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
        while True:
            try:
                coins = float(input(f'    Nhập số {Coin} bạn muốn đặt cho MỖI NHÂN VẬT: '))
                if coins > 0: break
                prints(247, 30, 30, 'Mức cược phải lớn hơn 0.')
            except ValueError:
                prints(247, 30, 30, 'Vui lòng nhập một số hợp lệ.')

        take_profit = float(input(f'    Chốt lời khi đạt được bao nhiêu {Coin} (nhập 0 để bỏ qua): '))
        stop_loss = float(input(f'    Cắt lỗ khi thua bao nhiêu {Coin} (nhập 0 để bỏ qua): '))
        consecutive_loss_stop = int(input('    Dừng tool sau bao nhiêu ván thua liên tiếp (nhập 0 để bỏ qua): '))
        
        prints(255, 165, 0, 'CÀI ĐẶT GẤP THẾP KHI THUA:')
        use_multiplier = input('    Bạn có muốn nhân tiền cược sau khi thua không? (y/n): ').lower() == 'y'
        loss_multiplier = 1.0
        if use_multiplier:
            while True:
                try:
                    loss_multiplier = float(input('    Nhân bao nhiêu lần sau mỗi lần thua? (ví dụ: 2): '))
                    if loss_multiplier >= 1.0: break
                    prints(247, 30, 30, 'Hệ số nhân phải lớn hơn hoặc bằng 1.')
                except ValueError:
                    prints(247, 30, 30, 'Vui lòng nhập một số hợp lệ.')

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
        # Chuyển đổi keys sang string để đảm bảo tương thích
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
        #bar = "▇" * bar_length
        prints(255, 255, 0, f'  {NV[int(i+1)]:<16} về nhất {wins:<3} lần ')
    prints(247, 255, 97, "═" * 47)

def select_betting_combination(data_top10_cdtd, data_top100_cdtd, game_count):
    """
    NÂNG CẤP LOGIC (V3): Phân tích xu hướng ngắn hạn (3 ván gần nhất)
    để quyết định cược theo Nóng (Top 3 Thắng) hay Lạnh (Top 3 Thua).
    Điều này giúp "bắt" các dạng bệt (streak) hoặc cầu ngắn hạn chính xác hơn.
    """
    try:
        # 1. Phân tích Top 100 (Xu hướng dài hạn)
        top_100_wins = {i + 1: count for i, count in enumerate(data_top100_cdtd[1])}
        
        # Sắp xếp các NV từ Lạnh nhất (ít thắng) đến Nóng nhất (nhiều thắng)
        sorted_by_wins = sorted(top_100_wins.items(), key=lambda item: item[1])
        
        # 2. Xác định 2 nhóm Nóng/Lạnh (Bao gồm tất cả 6 NV)
        # 3 NV thắng ít nhất trong 100 ván
        coldest_3 = [champ for champ, wins in sorted_by_wins[:3]]
        # 3 NV thắng nhiều nhất trong 100 ván
        hottest_3 = [champ for champ, wins in sorted_by_wins[3:]]

        # 3. Phân tích Top 10 (Xu hướng ngắn hạn)
        # Lấy 3 ván gần nhất (N=3). Vì N là số lẻ, sẽ không có tỷ số hòa (ví dụ 1.5-1.5).
        n_games = 3
        # Lấy N kết quả gần nhất (index 0, 1, 2)
        recent_winners = [int(w) for w in data_top10_cdtd[1][:n_games]]
        
        hot_score = 0
        cold_score = 0
        
        # Đếm xem 3 ván này thuộc nhóm Nóng hay Lạnh
        for winner in recent_winners:
            if winner in hottest_3:
                hot_score += 1
            elif winner in coldest_3: # 2 nhóm này bao gồm tất cả 6 NV
                cold_score += 1
        
        # 4. Ra quyết định (Không cần 'else' vì 3 ván không thể hòa)
        if hot_score > cold_score:
            # Xu hướng ngắn hạn (tỷ số 2-1 hoặc 3-0) nghiêng về nhóm Nóng
            # (Bao gồm cả trường hợp "bệt" 1 NV Nóng)
            #prints(0, 255, 255, f"  (Phân tích: {hot_score}/{n_games} ván gần nhất là Nóng -> Cược 3 Nóng nhất)")
            return hottest_3
        else: 
            # cold_score > hot_score (tỷ số 1-2 hoặc 0-3) nghiêng về nhóm Lạnh
            # (Bao gồm cả trường hợp "bệt" 1 NV Lạnh)
            #prints(0, 255, 255, f"  (Phân tích: {cold_score}/{n_games} ván gần nhất là Lạnh -> Cược 3 Lạnh nhất)")
            return coldest_3

    except Exception as e:
        # Lỗi: Báo chung chung và dùng chiến lược dự phòng
        prints(255, 0, 0, "Lỗi trong quá trình phân tích, chọn cược theo chiến lược dự phòng.")
        # Ghi lại lỗi ẩn
        prints(255, 100, 0, f"Chi tiết lỗi (đã ẩn): {type(e).__name__}")
        # Chiến lược dự phòng an toàn: Luân phiên 2 bộ
        fallback_sets = [[1, 2, 3], [4, 5, 6]]
        return fallback_sets[game_count % len(fallback_sets)]

def kiem_tra_kq_cdtd(headers, kqs_dat, ki):
    prints(0, 255, 37, f'Đang đợi kết quả của kì #{ki}')
    start_time = time.time()
    while True:
        try:
            data_top10_cdtd = top_10_cdtd(headers)
            # Chuyển đổi tất cả issue_id sang int để so sánh
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
        # Đảm bảo user-id là int
        user_id_val = int(headers['user-id'])
        json_data = {'user_id': user_id_val, 'source': 'home'}
        response = requests.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data).json()
        
        # Đảm bảo giá trị là float
        asset = {
            'USDT': float(response['data']['user_asset']['USDT']),
            'WORLD': float(response['data']['user_asset']['WORLD']),
            'BUILD': float(response['data']['user_asset']['BUILD'])
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
        
        # Chỉ hiển thị chuỗi thua từ 2 trở lên
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
                # Thông báo nghỉ được chuyển xuống logic nghỉ để hiển thị kì nghỉ chính xác
                pass
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
                # Đảm bảo ki là int
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
    
    # Khởi tạo loss_streaks từ 1 đến 9
    loss_streaks_init = {i: 0 for i in range(1, 10)}
    # Nếu consecutive_loss_stop lớn hơn 9, mở rộng dictionary
    if config['consecutive_loss_stop'] > 9:
         for i in range(10, config['consecutive_loss_stop'] + 1):
             loss_streaks_init[i] = 0

    stats = {
        'win': 0, 'lose': 0, 
        'consecutive_lose': 0,
        'consecutive_win': 0,
        'max_consecutive_win': 0,
        'loss_streaks': loss_streaks_init, # Sử dụng dictionary đã khởi tạo
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

        # --- LOGIC NGHỈ (REST LOGIC) ĐÃ SỬA LỖI ---
        if stats['games_to_skip'] > 0:
            # Lấy kì hiện tại (ván vừa kết thúc) và kì tiếp theo (sắp diễn ra, là kì sẽ bỏ qua)
            ki_hien_tai = int(data_top10_cdtd[0][0])
            ki_se_bo_qua = ki_hien_tai + 1
            
            prints(255, 255, 0, f"Ván này nghỉ, bỏ qua đặt cược cho Kì #{ki_se_bo_qua}. Còn lại {stats['games_to_skip']} ván nghỉ.")
            stats['games_to_skip'] -= 1
            
            prints(100, 100, 255, f"Đang chờ Kì #{ki_se_bo_qua} kết thúc...")
            
            # Chờ cho đến khi kì SAU KÌ BỎ QUA (ki_se_bo_qua + 1) bắt đầu
            # Điều này đảm bảo ki_se_bo_qua đã thực sự kết thúc.
            start_wait = time.time()
            while True:
                try:
                    latest_issue = int(top_10_cdtd(headers)[0][0])
                    # Khi latest_issue > ki_se_bo_qua (tức là = ki_se_bo_qua + 1)
                    if latest_issue > ki_se_bo_qua:
                        prints(0, 255, 0, f"\nKì #{ki_se_bo_qua} đã kết thúc. Chuẩn bị cho ván tiếp theo.")
                        break
                    
                    wait_time = time.time() - start_wait
                    prints(100, 100, 255, f"Đang chờ Kì #{ki_se_bo_qua} (ván hiện tại: {latest_issue})... {wait_time:.0f}s", end='\r')
                        
                except Exception:
                    prints(255, 0, 0, "Lỗi khi kiểm tra kì mới, đang thử lại...", end='\r')
                    pass
                time.sleep(5) # Chờ 5s giữa các lần kiểm tra
                
            time.sleep(10) # Thêm 10s đệm để đảm bảo ván mới ổn định
            continue
            
        game_count = stats['win'] + stats['lose']
        
        prints(247, 255, 97, "═" * 10 + "🔮 PHÂN TÍCH & CHỌN CƯỢC 🔮" + "═" * 9)
        # --- SỬ DỤNG LOGIC CƯỢC MỚI (V3) ---
        kqs_dat = select_betting_combination(data_top10_cdtd, data_top100_cdtd, game_count)

        prints(0, 246, 255, f'  BOT CHỌN ĐẶT QUÁN QUÂN: {", ".join([NV[kq] for kq in kqs_dat])}')
        prints(247, 255, 97, "═" * 47)
        
        next_ki = int(data_top10_cdtd[0][0]) + 1
        bet_cdtd(headers, next_ki, config, kqs_dat)
        
        result = kiem_tra_kq_cdtd(headers, kqs_dat, next_ki)
        
        if result:
            if stats['consecutive_lose'] > 0:
                streak_len = stats['consecutive_lose']
                # Ghi nhận chuỗi thua vừa bị ngắt
                if streak_len in stats['loss_streaks']:
                    stats['loss_streaks'][streak_len] += 1
                elif streak_len > 0:
                    # Mở rộng dictionary nếu chuỗi thua quá dài
                    stats['loss_streaks'][streak_len] = 1

            stats['win'] += 1
            stats['consecutive_win'] += 1
            if stats['consecutive_win'] > stats['max_consecutive_win']:
                stats['max_consecutive_win'] = stats['consecutive_win']
            stats['consecutive_lose'] = 0
            # Reset cược về mức ban đầu khi thắng
            config['current_coins'] = config['initial_coins']
        else:
            stats['lose'] += 1
            stats['consecutive_lose'] += 1
            stats['consecutive_win'] = 0
            # Gấp thếp khi thua (nếu bật)
            if config['use_multiplier']:
                config['current_coins'] *= config['loss_multiplier']
                config['current_coins'] = math.floor(config['current_coins'] * 10000) / 10000.0
        
        stats['games_played'] += 1

        if config['games_to_play'] > 0 and stats['games_played'] >= config['games_to_play']:
            prints(255, 165, 0, f"Đã chơi {stats['games_played']} ván. Bắt đầu nghỉ {config['games_to_rest']} ván.")
            stats['games_to_skip'] = config['games_to_rest']
            stats['games_played'] = 0
        
        time.sleep(10)

if __name__ == "__main__":
    # Bước 1: Chạy xác thực key
    is_authenticated, device_id, key_info = main_authentication()

    # Bước 2: Nếu xác thực thành công, chạy tool chính
    if is_authenticated:
        # Cập nhật thông báo sau khi xác thực
        if key_info and key_info.get('type') == 'vip':
            print(f"\n{luc}Xác thực Key VIP thành công. Bắt đầu chạy tool...{trang}")
        elif key_info and key_info.get('type') == 'free':
            print(f"\n{luc}Xác thực Key Free thành công. Bắt đầu chạy tool...{trang}")
        else:
            print(f"\n{luc}Xác thực thành công. Bắt đầu chạy tool...{trang}")
            
        time.sleep(2)
        try:
            main_cdtd()
        except KeyboardInterrupt:
            prints(255, 0, 0, "\nĐã dừng tool theo yêu cầu của người dùng.")
        except Exception as e:
            # --- ĐÃ CẬP NHẬT LOGIC BÁO LỖI ---
            # Ẩn traceback chi tiết theo yêu cầu
            # traceback.print_exc()
            prints(255, 0, 0, f"\nĐã xảy ra lỗi không mong muốn. Tool sẽ tự động thoát.")
            # Chỉ hiển thị loại lỗi, không hiển thị code
            prints(255, 100, 0, f"Chi tiết lỗi (đã ẩn): {type(e).__name__}")
            input("Nhấn Enter để thoát...")
    else:
        print(f"\n{do}Xác thực không thành công. Tool sẽ thoát.{trang}")
        sys.exit()
