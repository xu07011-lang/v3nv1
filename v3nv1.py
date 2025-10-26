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

import itertools
from collections import Counter, defaultdict, deque

# Tự động cài đặt thư viện nếu thiếu
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    import pytz
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.align import Align
    from rich.text import Text
except ImportError:
    print('__Đang cài đặt các thư viện cần thiết, vui lòng chờ...__')
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "colorama", "pytz", "rich"])
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

console = Console()

FREE_CACHE_FILE = 'free_key_cache.json'
VIP_CACHE_FILE = 'vip_cache.json'
HANOI_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
# URL Key chính thức (giữ nguyên)
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/keyxworkdf/main/keyxworkdf.txt"

def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

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
Tool xworld VTD (VIP PRO)
TIKTOK: @tdktool
══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.0001)

def get_device_id():
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
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        # print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
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
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
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
    data = {device_id: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(FREE_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)

def load_free_key_info():
    try:
        with open(FREE_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def check_saved_free_key(device_id):
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
    key_info = {'type': 'None', 'key': 'N/A', 'expiry': 'N/A'}

    if not device_id:
        print(f"{do}Không thể lấy thông tin Mã Máy. Vui lòng kiểm tra lại thiết bị.{trang}")
        return False, None, key_info

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
            print(f"{do}Lỗi file lưu key VIP. Vui lòng nhập lại key.{trang}")

    if check_saved_free_key(device_id):
        expiry_str = f"21:00 ngày {datetime.now(HANOI_TZ).strftime('%d/%m/%Y')}"
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn (Hết hạn lúc {expiry_str}). Mời bạn dùng tool...{trang}")
        key_info = {'type': 'Free', 'key': 'Active', 'expiry': expiry_str}
        time.sleep(2)
        return True, device_id, key_info

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
                if process_free_key(device_id):
                    expiry_str = f"21:00 ngày {datetime.now(HANOI_TZ).strftime('%d/%m/%Y')}"
                    key_info = {'type': 'Free', 'key': 'Active', 'expiry': expiry_str}
                    return True, device_id, key_info
                else:
                    sleep(1)

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except KeyboardInterrupt:
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

NV = {
    1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'
}
ALL_NV_IDS = list(NV.keys())

class SharedStateManager:
    # JSON Blob dùng chung cho việc phối hợp cược giữa nhiều người dùng
    SHARED_API_ENDPOINT = "https://api.jsonblob.com/api/jsonBlob/1286918519102373888" 

    def __init__(self, user_id):
        self.api_endpoint = self.SHARED_API_ENDPOINT
        self.user_id = user_id
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_shared_bets(self, issue_id):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get(str(issue_id), {})
            return {}
        except (requests.RequestException, json.JSONDecodeError):
            return {}

    def claim_bet(self, issue_id, bet_on_char):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            data = {}
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict): data = {}
                except json.JSONDecodeError: data = {}
            
            # Giới hạn lịch sử lưu trữ (chỉ giữ 5 ván gần nhất)
            current_issue_num = int(issue_id)
            keys_to_delete = [key for key in data.keys() if not key.isdigit() or int(key) < current_issue_num - 5]
            for key in keys_to_delete:
                del data[key]

            issue_key = str(issue_id)
            if issue_key not in data: data[issue_key] = {}
            
            # Claim NV cược
            data[issue_key][str(bet_on_char)] = self.user_id
            
            # Cập nhật JSON Blob
            requests.put(f"{self.api_endpoint}", data=json.dumps(data), headers=self.headers, timeout=5)
            return True
        except Exception:
            return False

# --- LOGIC NÂNG CẤP VIP PRO MỚI ---
class LogicEngineVipPro:
    def __init__(self, state_manager, history_min_size=20):
        self.history = deque(maxlen=200) # Lưu 200 ván gần nhất
        self.state_manager = state_manager
        self.history_min_size = history_min_size

    def add_result(self, winner_id):
        if winner_id in NV:
            self.history.append(winner_id)
            
    def _add_vote(self, candidates_dict, char_id, reason):
        """Hàm nội bộ để thêm "phiếu bầu" cho một ứng cử viên (để cược chống lại)."""
        if char_id not in candidates_dict:
            candidates_dict[char_id] = set()
        candidates_dict[char_id].add(reason)

    def _get_top_voted(self, candidates_dict, filter_by=None):
        """Hàm nội bộ để chọn ứng cử viên tốt nhất từ các phiếu bầu."""
        target_dict = candidates_dict
        
        # Lọc nếu có trạng thái ưu tiên (ví dụ: đang thua)
        if filter_by:
            filtered = {char: reasons for char, reasons in candidates_dict.items() if char in filter_by}
            if filtered: 
                target_dict = filtered
        
        if not target_dict: 
            return random.choice(ALL_NV_IDS)

        # Sắp xếp theo số phiếu, cao nhất trước
        sorted_candidates = sorted(target_dict.items(), key=lambda item: len(item[1]), reverse=True)
        
        # Lấy tất cả các ứng cử viên có cùng số phiếu cao nhất
        top_vote_count = len(sorted_candidates[0][1])
        top_choices = [char for char, reasons in sorted_candidates if len(reasons) == top_vote_count]
        
        # Trả về ngẫu nhiên một trong số top để phá vỡ thế cân bằng
        return random.choice(top_choices)

    def analyze_and_select(self, issue_id, consecutive_losses=0):
        """
        Phân tích lịch sử và chọn nhân vật để cược CHỐNG LẠI (bet 'not_winner').
        Logic thay đổi dựa trên chuỗi thua (consecutive_losses) để tối đa hóa an toàn.
        """
        
        # --- Giai đoạn 1: Khởi động (Chưa đủ dữ liệu) ---
        if len(self.history) < self.history_min_size:
            if len(self.history) > 0:
                # An toàn: cược chống lại người vừa thắng
                return self.history[-1] 
            else:
                # Hoàn toàn không có dữ liệu
                return random.choice(ALL_NV_IDS)

        # candidates: dict lưu {char_id: set(lý do tại sao nên cược chống lại nó)}
        candidates = {}
        
        # === BẮT ĐẦU CÁC MODULE PHÂN TÍCH ===
        
        # --- Module 1: Phân tích "Lạnh" (Cold Analysis) ---
        # Tìm nhân vật đã không thắng trong thời gian dài nhất.
        # Lý luận: Nhân vật "lạnh" nhất có ít khả năng thắng nhất.
        last_seen_at = {char_id: -1 for char_id in ALL_NV_IDS}
        for i, char_id in enumerate(reversed(self.history)):
            if last_seen_at[char_id] == -1:
                last_seen_at[char_id] = i
        
        # Xử lý các nhân vật chưa từng xuất hiện (rất "lạnh")
        never_seen_distance = len(self.history) + 1
        for char_id in ALL_NV_IDS:
            if last_seen_at[char_id] == -1:
                last_seen_at[char_id] = never_seen_distance
                
        sorted_cold = sorted(last_seen_at.items(), key=lambda item: item[1], reverse=True)
        
        coldest_char = sorted_cold[0][0]
        second_coldest_char = sorted_cold[1][0]
        self._add_vote(candidates, coldest_char, "Coldest (Lạnh nhất)")
        self._add_vote(candidates, second_coldest_char, "Second Coldest (Lạnh nhì)")

        # --- Module 2: Phân tích "Nóng" (Hot Streak Breaker) ---
        # Tìm nhân vật đang có chuỗi thắng.
        # Lý luận: Chuỗi thắng càng dài, khả năng bị phá vỡ càng cao.
        if self.history[-1] == self.history[-2]:
            hot_char = self.history[-1]
            # Phiếu bầu rất mạnh để cược chống lại
            self._add_vote(candidates, hot_char, "Hot Streak x2 (Chuỗi 2)")
            
            if len(self.history) >= 3 and self.history[-1] == self.history[-2] == self.history[-3]:
                # Phiếu bầu CỰC KỲ mạnh (chuỗi 3 rất hiếm)
                self._add_vote(candidates, hot_char, "Hot Streak x3 (Chuỗi 3)")

        # --- Module 3: Phân tích Tần suất (Frequency Analysis) ---
        # Tìm nhân vật thắng ÍT NHẤT trong lịch sử.
        # Lý luận: Nhân vật ít thắng nhất có thể là "kẻ yếu" của game.
        freq = Counter(self.history)
        min_freq = float('inf')
        least_frequent_char = -1
        for char_id in ALL_NV_IDS:
            if freq.get(char_id, 0) < min_freq:
                min_freq = freq.get(char_id, 0)
                least_frequent_char = char_id
        if least_frequent_char != -1:
            self._add_vote(candidates, least_frequent_char, "Least Frequent (Ít thắng nhất)")
            
        # --- Module 4: Phân tích Chuyển tiếp (Transition Analysis) ---
        # Sau khi ván (A, B) xảy ra, ván C nào ÍT XUẤT HIỆN nhất?
        # Lý luận: Cược chống lại kết quả ít có khả năng xảy ra nhất theo cặp.
        if len(self.history) >= 2:
            last_winner = self.history[-1]
            prev_winner = self.history[-2]
            transitions = defaultdict(int)
            
            for i in range(len(self.history) - 2):
                if self.history[i] == prev_winner and self.history[i+1] == last_winner:
                    transitions[self.history[i+2]] += 1
            
            if transitions: # Chỉ chạy nếu tìm thấy cặp (A, B)
                min_transition_count = float('inf')
                least_likely_next = -1
                for char_id in ALL_NV_IDS:
                    if transitions.get(char_id, 0) < min_transition_count:
                        min_transition_count = transitions.get(char_id, 0)
                        least_likely_next = char_id
                if least_likely_next != -1:
                     self._add_vote(candidates, least_likely_next, "Least Likely Transition (Ít chuyển tiếp nhất)")

        # === KẾT THÚC CÁC MODULE PHÂN TÍCH ===


        # --- Giai đoạn 2: Ra Quyết Định (Dựa trên trạng thái Thắng/Thua) ---
        
        final_choice = -1
        
        if consecutive_losses == 0:
            # --- Trạng thái 0: Bình thường (Đang thắng) ---
            # Cược linh hoạt, chọn ứng cử viên có nhiều phiếu bầu nhất từ tất cả các module.
            final_choice = self._get_top_voted(candidates)
            
        elif consecutive_losses == 1:
            # --- Trạng thái 1: Thua 1 ván ---
            # Ưu tiên sự an toàn. 
            # Ưu tiên cược chống lại nhân vật "Lạnh" hoặc "Ít thắng nhất".
            priority_chars = [c for c, reasons in candidates.items() 
                              if "Coldest (Lạnh nhất)" in reasons or "Least Frequent (Ít thắng nhất)" in reasons]
            
            final_choice = self._get_top_voted(candidates, filter_by=priority_chars)
            
        elif consecutive_losses >= 2:
            # --- Trạng thái 2: "NGUY HIỂM" (Thua 2+ ván) ---
            # Mục tiêu: SỐNG SÓT. Sử dụng logic an toàn nhất tuyệt đối.
            
            # Ưu tiên 1: Cược phá chuỗi 3 (cực hiếm).
            hot_x3_chars = [c for c, reasons in candidates.items() if "Hot Streak x3 (Chuỗi 3)" in reasons]
            if hot_x3_chars:
                final_choice = hot_x3_chars[0]
            
            # Ưu tiên 2: Cược phá chuỗi 2.
            elif "Hot Streak x2 (Chuỗi 2)" in str(candidates):
                 hot_x2_chars = [c for c, reasons in candidates.items() if "Hot Streak x2 (Chuỗi 2)" in reasons]
                 if hot_x2_chars:
                     final_choice = hot_x2_chars[0]

            # Ưu tiên 3: Nếu không có chuỗi nóng, cược chống lại nhân vật "Lạnh nhất".
            # Đây là lựa chọn an toàn nhất trong tình huống hỗn loạn.
            else:
                final_choice = coldest_char

        
        # --- Giai đoạn 3: Kiểm tra Phối hợp Đa người dùng ---
        shared_bets = self.state_manager.get_shared_bets(issue_id)
        claimed_chars = [int(k) for k in shared_bets.keys()]

        if final_choice not in claimed_chars:
            # Lựa chọn tốt nhất của chúng ta chưa ai chọn -> Claim
            self.state_manager.claim_bet(issue_id, final_choice)
            return final_choice
        else:
            # Lựa chọn tốt nhất (final_choice) đã bị người khác claim.
            # Tìm lựa chọn tốt thứ 2, thứ 3...
            
            # Sắp xếp lại tất cả các ứng cử viên theo số phiếu
            ranked_candidates = sorted(candidates.items(), key=lambda item: len(item[1]), reverse=True)
            
            for char, votes in ranked_candidates:
                if char not in claimed_chars:
                    # Tìm thấy lựa chọn tốt tiếp theo chưa bị claim
                    self.state_manager.claim_bet(issue_id, char)
                    return char
            
            # Nếu TẤT CẢ các ứng cử viên có phiếu bầu đều đã bị claim
            # Chọn một nhân vật bất kỳ chưa bị claim
            unclaimed_fallback = [c for c in ALL_NV_IDS if c not in claimed_chars]
            if unclaimed_fallback:
                fallback_choice = random.choice(unclaimed_fallback)
                self.state_manager.claim_bet(issue_id, fallback_choice)
                return fallback_choice
            else:
                # Trường hợp cực hiếm: Cả 6 NV đều bị claim.
                # Vẫn cược vào lựa chọn ban đầu (chấp nhận trùng).
                return final_choice
# --- KẾT THÚC LOGIC NÂNG CẤP VIP PRO ---

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def format_time(seconds):
    if seconds < 0: return "0 ngày 0 giờ 0 phút"
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} ngày {hours} giờ {minutes} phút"

def add_log(logs_deque, message):
    hanoi_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    timestamp = datetime.now(hanoi_tz).strftime('%H:%M:%S')
    logs_deque.append(f"[grey70]{timestamp}[/grey70] {message}")

# --- DASHBOARD HOÀN HẢO (FIXED LOGIC LỊCH SỬ) ---
def generate_dashboard(config, stats, wallet_asset, logs, coin_type, status_message, key_info, history_deque) -> Panel:
    total_games = stats['win'] + stats['lose']
    win_rate = (stats['win'] / total_games * 100) if total_games > 0 else 0
    profit = wallet_asset.get(coin_type, 0) - stats['asset_0']
    profit_str = f"[bold green]+{profit:,.4f}[/bold green]" if profit >= 0 else f"[bold red]{profit:,.4f}[/bold red]"

    stats_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    stats_table.add_column(style="cyan"); stats_table.add_column(style="white")
    stats_table.add_row("Phiên Bản", "VIP ")
    stats_table.add_row("Lợi Nhuận", f"{profit_str} {coin_type}")
    stats_table.add_row("Tổng Trận", str(total_games))
    stats_table.add_row("Thắng / Thua", f"[green]{stats['win']}[/green] / [red]{stats['lose']}[/red] ({win_rate:.2f}%)")
    stats_table.add_row("Chuỗi Thắng", f"[green]{stats['streak']}[/green] (Max: {stats['max_streak']})")
    stats_table.add_row("Chuỗi Thua", f"[red]{stats['lose_streak']}[/red]")
    lt_stats = stats['consecutive_loss_counts']
    stats_table.add_row("Tổng Thua L.Tiếp (1/2/3/4)", f"{lt_stats[1]} / {lt_stats[2]} / {lt_stats[3]} / {lt_stats[4]}")

    config_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    config_table.add_column(style="cyan"); config_table.add_column(style="yellow")
    config_table.add_row("Cược Cơ Bản", f"{config['bet_amount0']} {coin_type}")
    config_table.add_row("Hệ Số Gấp", str(config['heso']))
    config_table.add_row("Chế Độ Nghỉ", f"Chơi {config['delay1']} nghỉ {config['delay2']}")
    
    balance_table = Table(title="Số Dư", show_header=True, header_style="bold magenta", box=None)
    balance_table.add_column("Loại Tiền", style="cyan", justify="left")
    balance_table.add_column("Số Lượng", style="white", justify="right")
    balance_table.add_row("BUILD", f"{wallet_asset.get('BUILD', 0.0):,.4f}")
    balance_table.add_row("WORLD", f"{wallet_asset.get('WORLD', 0.0):,.4f}")
    balance_table.add_row("USDT", f"{wallet_asset.get('USDT', 0.0):,.4f}")
    
    key_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    key_table.add_column(style="cyan"); key_table.add_column(style="white")
    
    if key_info.get('type') == 'VIP':
        key_table.add_row("Loại Key", "[bold gold1]VIP[/bold gold1]")
        key_table.add_row("Key", f"[gold1]{key_info.get('key', 'N/A')}[/gold1]")
        key_table.add_row("Hạn Dùng", f"[yellow]{key_info.get('expiry', 'N/A')}[/yellow]")
    elif key_info.get('type') == 'Free':
        hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(hcm_tz)
        expiry_time_today = now.replace(hour=21, minute=0, second=0, microsecond=0)
        
        if expiry_time_today < now:
            expiry_time = now + timedelta(days=1)
            expiry_time = expiry_time.replace(hour=21, minute=0, second=0, microsecond=0)
        else:
            expiry_time = expiry_time_today
        
        delta = expiry_time - now
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        key_table.add_row("Loại Key", "[bold green]Free[/bold green]")
        key_table.add_row("Hạn Dùng", "[green]21:00:00 hàng ngày[/green]")
        key_table.add_row("Thời gian còn", f"[yellow]{countdown}[/yellow]")
    
    key_panel = Panel(key_table, title="[bold]Thông Tin Key[/bold]", border_style="blue")
    
    # --- Bảng Phân Tích 10 Ván Gần Nhất (FIXED LỖI THỨ TỰ) ---
    last_10_history = list(history_deque)[-10:]
    last_10_freq = Counter(last_10_history)
    
    history_str_parts = []
    # FIX: Đảo ngược list để hiển thị kết quả từ MỚI NHẤT -> CŨ NHẤT
    for h in reversed(last_10_history): 
        history_str_parts.append(f"[cyan]{NV.get(h, '?').split(' ')[0]}[/cyan]")
    history_str = " ".join(history_str_parts)
    
    freq_table = Table(show_header=False, show_edge=False, box=None, padding=0)
    freq_table.add_column(style="yellow"); freq_table.add_column(style="white", justify="right")
    freq_table.add_column(width=2);
    freq_table.add_column(style="yellow"); freq_table.add_column(style="white", justify="right")
    
    freq_table.add_row(
        f"{NV[1].split(' ')[0]}:", f"{last_10_freq.get(1, 0)}", "",
        f"{NV[2].split(' ')[0]}:", f"{last_10_freq.get(2, 0)}",
    )
    freq_table.add_row(
        f"{NV[3].split(' ')[0]}:", f"{last_10_freq.get(3, 0)}", "",
        f"{NV[4].split(' ')[0]}:", f"{last_10_freq.get(4, 0)}",
    )
    freq_table.add_row(
        f"{NV[5].split(' ')[0]}:", f"{last_10_freq.get(5, 0)}", "",
        f"{NV[6].split(' ')[0]}:", f"{last_10_freq.get(6, 0)}",
    )
    
    history_panel_content = Table.grid(expand=True)
    history_panel_content.add_row(f"[bold]Lịch sử 10 ván (Mới nhất -> Cũ nhất):[/bold] {history_str if last_10_history else 'Đang chờ...'}")
    history_panel_content.add_row(Align.center(freq_table))
    
    history_panel = Panel(history_panel_content, title="[bold]Phân Tích 10 Ván Gần Nhất[/bold]", border_style="blue")
    # --- Kết thúc bảng Phân Tích ---

    info_layout = Table.grid(expand=True)
    info_layout.add_column(ratio=1); info_layout.add_column(ratio=1)
    
    info_layout.add_row(Panel(stats_table, title="[bold]Thống Kê[/bold]", border_style="blue"), Panel(config_table, title="[bold]Cấu Hình[/bold]", border_style="blue"))
    info_layout.add_row(Panel(balance_table, border_style="blue"), key_panel)

    log_panel = Panel("\n".join(reversed(logs)), title="[bold]Nhật Ký Hoạt Động[/bold]", border_style="green", height=12)
    
    status_panel = Panel(Align.center(Text(status_message, justify="center")), title="[bold]Trạng Thái[/bold]", border_style="yellow", height=3)
    
    main_grid = Table.grid(expand=True)
    main_grid.add_row(status_panel)
    main_grid.add_row(info_layout)
    main_grid.add_row(history_panel) 
    main_grid.add_row(log_panel)
    
    dashboard = Panel(
        main_grid,
        title=f"[bold gold1]VTD VIP[/bold gold1] - Thời gian chạy: {format_time(time.time() - config['start_time'])}",
        border_style="bold magenta"
    )
    return dashboard
# --- KẾT THÚC DASHBOARD HOÀN HẢO ---

def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        console.print(f"[cyan]Tìm thấy file dữ liệu đã lưu. Bạn có muốn sử dụng không? (y/n): [/cyan]", end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    console.print(f"\n[yellow]Hướng dẫn lấy link:\n1. Truy cập xworld.io và đăng nhập\n2. Vào game 'Chạy đua tốc độ'\n3. Copy link của trang game và dán vào đây[/yellow]")
    console.print(f"[cyan]📋 Vui lòng nhập link của bạn: [/cyan]", end=''); link = input()
    try:
        user_id = re.search(r'userId=(\d+)', link).group(1)
        secret_key = re.search(r'secretKey=([a-zA-Z0-9]+)', link).group(1)
    except AttributeError:
        console.print(f"[bold red]❌ Link không hợp lệ hoặc thiếu thông tin User ID/Secret Key.[/bold red]")
        sys.exit()
    
    console.print(f"[green]    ✓ Lấy thông tin thành công! User ID: {user_id}[/green]")
    json_data = {'user-id': user_id, 'user-secret-key': secret_key}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def populate_initial_history(s, headers, logic_engine):
    console.print(f"\n[green]Đang lấy dữ liệu lịch sử ban đầu...[/green]")
    try:
        # Lấy 100 ván gần nhất
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues?limit=100', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            # Đảo ngược để nạp vào deque theo thứ tự từ cũ đến mới
            for issue_data in reversed(response['data']['recent_10']):
                if issue_data['result']:
                    logic_engine.add_result(issue_data['result'][0])
            console.print(f"[green]✓ Nạp thành công lịch sử {len(response['data']['recent_10'])} ván.[/green]"); return True
    except Exception as e: console.print(f"[red]Lỗi khi nạp lịch sử: {e}[/red]")
    return False

def fetch_latest_issue_info(s, headers):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues?limit=1', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            latest_issue = response['data']['recent_10'][0]
            return latest_issue['issue_id'], latest_issue
    except Exception: return None, None
    return None, None

def check_issue_result(s, headers, kq, ki):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues?limit=10', headers=headers, timeout=5).json()
        for issue in response['data']['recent_10']:
            if int(issue['issue_id']) == int(ki):
                actual_winner = issue['result'][0] 
                return actual_winner != kq, actual_winner
    except Exception: return None, None
    return None, None

def user_asset(s, headers):
    while True:
        try:
            json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
            return s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data, timeout=5).json()['data']['user_asset']
        except Exception as e:
            console.print(f"[red]Lỗi khi lấy số dư: {e}. Thử lại sau 2s...[/red]"); time.sleep(2)

def bet_cdtd(s, headers, ki, kq, Coin, bet_amount, logs):
    try:
        # Thêm sai số ngẫu nhiên nhỏ để tránh bị nhận diện bởi thuật toán game
        bet_amount_randomized = round(bet_amount * random.uniform(0.995, 1.005), 8)
        
        # bet_group: 'not_winner' (cược né quán quân)
        json_data = {
            'issue_id': int(ki), 
            'bet_group': 'not_winner', 
            'asset_type': Coin, 
            'athlete_id': kq, # NV bị né (ta cược nó KHÔNG phải là quán quân)
            'bet_amount': bet_amount_randomized
        }
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data, timeout=10).json()
        
        return response
    except requests.exceptions.RequestException as e:
        add_log(logs, f"[red]Lỗi mạng khi đặt cược:[/red] [white]{e}[/white]")
        return None

def get_user_input(prompt, input_type=float):
    while True:
        try:
            console.print(prompt, end="")
            value = input_type(input())
            # Đảm bảo số cược ban đầu, hệ số và số ván là hợp lệ
            if input_type == float and value <= 0:
                console.print("[bold red]Giá trị phải lớn hơn 0.[/bold red]")
                continue
            if input_type == int and value < 0:
                console.print("[bold red]Giá trị phải là số nguyên không âm.[/bold red]")
                continue
            return value
        except ValueError:
            console.print("[bold red]Định dạng không hợp lệ, vui lòng nhập lại một số.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Đã xảy ra lỗi: {e}. Vui lòng thử lại.[/bold red]")

# --- MAIN GAME LOOP ---
def main_cdtd(device_id, key_info):
    s = requests.Session()
    data = load_data_cdtd()
    headers = {'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'], 'user-agent': 'Mozilla/5.0'}

    clear_screen()
    
    asset = user_asset(s, headers)
    console.print(f"[cyan]Chọn loại tiền bạn muốn chơi:[/cyan]\n  1. USDT\n  2. BUILD\n  3. WORLD")
    while True:
        console.print(f'[cyan]Nhập lựa chọn (1/2/3): [/cyan]', end="")
        x = input()
        if x in ['1', '2', '3']: Coin = ['USDT', 'BUILD', 'WORLD'][int(x)-1]; break
        else: console.print(f"[red]Lựa chọn không hợp lệ, vui lòng nhập lại...[/red]")

    bet_amount0 = get_user_input(f'[cyan]Nhập số {Coin} muốn đặt ban đầu: [/cyan]', float)
    heso = get_user_input(f'[cyan]Nhập hệ số cược sau khi thua: [/cyan]', float) 
    delay1 = get_user_input(f'[cyan]Chơi bao nhiêu ván thì nghỉ (0 hoặc 999 nếu không nghỉ): [/cyan]', int)
    delay2 = get_user_input(f'[cyan]Nghỉ trong bao nhiêu ván (nếu delay1 > 0): [/cyan]', int)
    
    user_unique_id = hashlib.sha256(device_id.encode()).hexdigest()[:8]
    state_manager = SharedStateManager(user_unique_id)
    logic_engine = LogicEngineVipPro(state_manager) 

    stats = {
        'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'lose_streak': 0, 
        'asset_0': asset.get(Coin, 0), 'consecutive_loss_counts': defaultdict(int)
    }
    config = {'bet_amount0': bet_amount0, 'heso': heso, 'delay1': delay1, 'delay2': delay2, 'start_time': time.time()}
    logs = deque(maxlen=10)
    tong_van = 0
    rest_until_round = 0 
    
    attempted_bets = deque(maxlen=100)

    # Nạp lịch sử ban đầu
    populate_initial_history(s, headers, logic_engine); time.sleep(2)
    last_known_id, _ = fetch_latest_issue_info(s, headers)
    if not last_known_id:
        console.print(f"[red]Không thể lấy ID ván đầu tiên. Vui lòng kiểm tra lại mạng và API.[/red]")
        sys.exit()

    with Live(generate_dashboard(config, stats, asset, logs, Coin, "", key_info, logic_engine.history), console=console, screen=True, auto_refresh=False) as live:
        while True:
            try:
                current_asset = user_asset(s, headers)
                status_msg = f"Đang chờ ván #{last_known_id + 1} bắt đầu..."
                live.update(generate_dashboard(config, stats, current_asset, logs, Coin, status_msg, key_info, logic_engine.history), refresh=True)

                # --- 1. Đợi ván mới ---
                newly_completed_id = last_known_id
                while newly_completed_id == last_known_id:
                    time.sleep(1)
                    newly_completed_id, newly_completed_issue_data = fetch_latest_issue_info(s, headers)
                    if newly_completed_id is None: newly_completed_id = last_known_id

                last_known_id = newly_completed_id
                
                # Cập nhật lịch sử với kết quả ván vừa xong
                if newly_completed_issue_data and 'result' in newly_completed_issue_data and newly_completed_issue_data['result']:
                    logic_engine.add_result(newly_completed_issue_data['result'][0])

                # --- 2. Xử lý trạng thái nghỉ ngơi bắt buộc sau khi thua ---
                if rest_until_round > last_known_id:
                    rounds_remaining = rest_until_round - last_known_id
                    rest_msg = f"[yellow]💤 Đang nghỉ sau ván thua. Còn {rounds_remaining} ván (đến #{rest_until_round}).[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info, logic_engine.history), refresh=True)
                    time.sleep(30) 
                    continue 
                else:
                    if rest_until_round != 0:
                        add_log(logs, f"[green]✅ Đã nghỉ ngơi xong. Bắt đầu chơi lại.[/green]")
                        rest_until_round = 0 
                
                # --- 3. Xử lý chế độ nghỉ cố định (Delay 1, Delay 2) ---
                tong_van += 1
                cycle = delay1 + delay2
                is_resting = False
                if delay1 > 0 and cycle > 0:
                    pos = (tong_van - 1) % cycle
                    is_resting = pos >= delay1
                
                if is_resting:
                    rest_msg = f"[yellow]💤 Tạm nghỉ theo cấu hình. Tiếp tục sau {cycle - pos} ván nữa.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info, logic_engine.history), refresh=True)
                    time.sleep(30); continue

                # --- 4. Logic Chống Bắt Bài (Bỏ qua ngẫu nhiên) ---
                if random.random() < 0.05: # Tỷ lệ 5% bỏ qua ván
                    rest_msg = f"[yellow]💤 Bỏ qua ván này ngẫu nhiên để thay đổi hành vi (5% Skip).[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info, logic_engine.history), refresh=True)
                    time.sleep(30); continue

                # --- 5. Đặt Cược ---
                bet_amount = bet_amount0 * (heso ** stats['lose_streak'])
                
                # Random delay trước khi cược (Ao nhây)
                pre_bet_delay = random.uniform(2, 5)
                time.sleep(pre_bet_delay)

                # Lấy ID ván sẽ cược
                current_betting_issue_id = last_known_id + 1
                
                # Tránh cược lại cùng một ván
                if current_betting_issue_id in attempted_bets:
                    log_msg = f"[yellow]⚠️ Đã thử cược ván #{current_betting_issue_id}. Bỏ qua cược lặp.[/yellow]"
                    add_log(logs, log_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, log_msg, key_info, logic_engine.history), refresh=True)
                    time.sleep(10)
                    continue
                attempted_bets.append(current_betting_issue_id)

                # === THAY ĐỔI QUAN TRỌNG: TRUYỀN `stats['lose_streak']` VÀO LOGIC ===
                # Chọn NV để né (KQ) bằng Logic VIP PRO (đã nhận biết chuỗi thua)
                kq = logic_engine.analyze_and_select(current_betting_issue_id, stats['lose_streak'])
                
                log_msg = f"[yellow]Cược né[/yellow] [white]'{NV.get(kq, kq)}'[/white] [yellow]với[/yellow] [white]{bet_amount:,.4f} {Coin}[/white] [yellow](Chuỗi thua: {stats['lose_streak']})[/yellow]"
                add_log(logs, log_msg)
                
                response = bet_cdtd(s, headers, current_betting_issue_id, kq, Coin, bet_amount, logs)
                
                if response and response.get('code') == 0:
                    start_wait_time = time.time()
                    
                    # --- 6. Đợi và kiểm tra kết quả ---
                    while True:
                        result, actual_winner = check_issue_result(s, headers, kq, current_betting_issue_id)
                        if result is not None: break
                        
                        elapsed = int(time.time() - start_wait_time)
                        wait_message = f"⏳ Đợi KQ kì #{current_betting_issue_id}: {elapsed}s. Cược né '{NV.get(kq, kq)}' với [yellow]{bet_amount:,.4f} {Coin}[/yellow]"
                        live.update(generate_dashboard(config, stats, current_asset, logs, Coin, wait_message, key_info, logic_engine.history), refresh=True)
                        time.sleep(1)

                    if result:
                        stats['win'] += 1; stats['streak'] += 1; stats['lose_streak'] = 0
                        stats['max_streak'] = max(stats['max_streak'], stats['streak'])
                        log_msg = (f"[bold green]THẮNG[/bold green] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[cyan]{NV.get(actual_winner, actual_winner)}[/cyan]'")
                        add_log(logs, log_msg)
                    else:
                        stats['lose'] += 1; stats['lose_streak'] += 1; stats['streak'] = 0
                        stats['consecutive_loss_counts'][stats['lose_streak']] += 1
                        log_msg = (f"[bold red]THUA[/bold red] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[red]{NV.get(actual_winner, actual_winner)}[/red]' (Trùng)")
                        add_log(logs, log_msg)
                        
                        # --- Kích hoạt nghỉ ngơi (3-6 ván) sau khi thua ---
                        rounds_to_rest = random.randint(3, 6)
                        rest_until_round = current_betting_issue_id + rounds_to_rest
                        add_log(logs, f"[yellow]Nghỉ ngơi {rounds_to_rest} ván (đến ván #{rest_until_round}) do thua.[/yellow]")
                        
                else:
                    if response:
                        log_msg = f"[red]Lỗi cược ván #{current_betting_issue_id}:[/red] [white]{response.get('msg', 'Không rõ lỗi')}[/white]"
                        add_log(logs, log_msg)
                
                # --- 7. Cập nhật và đợi ---
                final_asset = user_asset(s, headers)
                live.update(generate_dashboard(config, stats, final_asset, logs, Coin, "", key_info, logic_engine.history), refresh=True)
                time.sleep(random.uniform(5, 10))

            except Exception as e:
                add_log(logs, f"[bold red]Lỗi nghiêm trọng: {e}. Sẽ thử lại sau 10s[/bold red]")
                time.sleep(10)

def show_banner():
    clear_screen()
    banner_text = Text.from_markup(f"""
[bold cyan]
 ████████╗██████╗ ██╗  ██╗
 ╚══██╔══╝██╔══██╗██║ ██╔╝
    ██║   ██║  ██║█████╔╝
    ██║   ██║  ██║██╔═██╗
    ██║   ██████╔╝██║  ██╗
    ╚═╝   ╚═════╝ ╚═╝  ╚═╝
[/bold cyan]
    """, justify="center")
    console.print(Panel(banner_text, border_style="magenta"))
    console.print(Align.center("[bold gold1]CHẠY ĐUA VIP PRO  - Khởi tạo thành công![/bold gold1]\n"))
    time.sleep(3)


if __name__ == "__main__":
    authentication_successful, device_id, key_info = main_authentication()

    if authentication_successful:
        show_banner()
        main_cdtd(device_id, key_info)
    else:
        print(f"\n{do}Xác thực không thành công. Vui lòng chạy lại tool.{end}")
        sys.exit()
