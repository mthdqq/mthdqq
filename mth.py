import os
import socket
import time
import random
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import speedtest
from datetime import datetime

# Thư mục lưu log
log_dir = os.path.join(os.getenv("HOME", "/tmp"), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'network_tool_log.txt')

# Ghi log
def log_message(message):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

# Hiển thị logo và thông báo tác giả
def display_logo():
    print(colored("""
    ███╗   ███╗████████╗██╗  ██╗
    ████╗ ████║╚══██╔══╝██║  ██║
    ██╔████╔██║   ██║   ███████║
    ██║╚██╔╝██║   ██║   ██╔══██║
    ██║ ╚═╝ ██║   ██║   ██║  ██║
    ╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝
    Công cụ kiểm tra mạng - Hoàn Chỉnh
    """, 'cyan'))
    print(colored("""
    === Công cụ được thiết kế bởi: Mai Tỗ Hữu (MTH TCM) ===
    - Liên hệ: zalo 0359379411
    - Mục đích: Kiểm tra và đánh giá hiệu suất mạng.
    """, 'green'))

# Hiển thị cảnh báo
def display_warning():
    print(colored("""
    === CẢNH BÁO ===
    - Một số thao tác có thể gây mất kết nối mạng hoặc giảm hiệu suất mạng.
    - Các chức năng kiểm tra chịu tải và tiêu tốn dữ liệu có thể làm gián đoạn dịch vụ mạng.
    - Vui lòng đảm bảo rằng bạn đã hiểu rõ rủi ro và sử dụng công cụ này một cách có trách nhiệm.
    """, 'red'))

# Kiểm tra tốc độ mạng
def test_speed():
    print(colored("\n=== Kiểm tra tốc độ mạng ===", 'yellow'))
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Mbps
        upload_speed = st.upload() / 1_000_000  # Mbps
        ping_latency = st.results.ping  # ms
        print(colored(f"Tốc độ tải xuống: {download_speed:.2f} Mbps", 'green'))
        print(colored(f"Tốc độ tải lên: {upload_speed:.2f} Mbps", 'green'))
        print(colored(f"Ping: {ping_latency} ms", 'green'))
        log_message(f"Speed test: Download={download_speed:.2f} Mbps, Upload={upload_speed:.2f} Mbps, Ping={ping_latency} ms")
    except Exception as e:
        print(colored(f"Lỗi khi kiểm tra tốc độ mạng: {e}", 'red'))
        log_message(f"Error testing speed: {e}")

# Quét thiết bị trong mạng LAN
def scan_network():
    print(colored("\n=== Quét thiết bị trong mạng LAN ===", 'yellow'))
    ip_range = input("Nhập dải IP mạng LAN (ví dụ: 192.168.1.0/24): ").strip()
    
    try:
        result = subprocess.run(
            ['fping', '-g', ip_range], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(colored(f"Các thiết bị trong mạng: \n{result.stdout}", 'green'))
            log_message(f"Network scan completed: {result.stdout}")
        else:
            print(colored("Không thể quét mạng, vui lòng kiểm tra lại dải IP hoặc cài đặt fping.", 'red'))
            log_message("Error during network scan.")
    except Exception as e:
        print(colored(f"Lỗi khi quét mạng: {e}", 'red'))
        log_message(f"Error scanning network: {e}")

# Kiểm tra chịu tải mạng (stress test)
def stress_test(target, duration=30, connections=100, protocol="TCP"):
    print(colored(f"\n=== Kiểm tra chịu tải mạng trên {target} ===", 'yellow'))
    print(colored("CẢNH BÁO: Kiểm tra chịu tải có thể làm gián đoạn kết nối mạng!", 'red'))
    input(colored("Nhấn Enter để tiếp tục nếu bạn đồng ý...", 'yellow'))
    
    stop_time = time.time() + duration

    def tcp_stress():
        try:
            while time.time() < stop_time:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((target, 80))
                    s.sendall(b"GET / HTTP/1.1\r\nHost: target\r\n\r\n")
                    s.recv(1024)
        except Exception as e:
            pass  # Bỏ qua lỗi khi quá tải

    def udp_stress():
        try:
            while time.time() < stop_time:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.sendto(b"A" * 1024, (target, 80))
        except Exception as e:
            pass

    func = tcp_stress if protocol.upper() == "TCP" else udp_stress
    with ThreadPoolExecutor(max_workers=connections) as executor:
        executor.submit(func)
    
    print(colored("Hoàn thành kiểm tra chịu tải!", 'green'))
    log_message(f"Stress test completed: {target}, Duration={duration}s, Connections={connections}, Protocol={protocol}")

# Kiểm tra băng thông (Bandwidth Saturation)
def bandwidth_saturation(target, duration=30):
    print(colored(f"\n=== Kiểm tra băng thông trên {target} ===", 'yellow'))
    print(colored("CẢNH BÁO: Kiểm tra băng thông có thể làm chậm toàn bộ mạng!", 'red'))
    input(colored("Nhấn Enter để tiếp tục nếu bạn đồng ý...", 'yellow'))
    
    stop_time = time.time() + duration

    def send_data():
        try:
            while time.time() < stop_time:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((target, 80))
                    s.sendall(b"A" * 4096)
        except Exception as e:
            pass  # Bỏ qua lỗi

    with ThreadPoolExecutor(max_workers=50) as executor:
        for _ in range(50):  # Gửi nhiều luồng dữ liệu cùng lúc
            executor.submit(send_data)
    
    print(colored("Hoàn thành kiểm tra băng thông!", 'green'))
    log_message(f"Bandwidth saturation completed: {target}, Duration={duration}s")

# Tiêu tốn dữ liệu 4G
def consume_4g_data(limit_gb=100):
    print(colored("\n=== Tiêu tốn dữ liệu 4G (phát WiFi) ===", 'yellow'))
    print(colored("CẢNH BÁO: Tiêu tốn dữ liệu có thể gây mất toàn bộ dung lượng 4G!", 'red'))
    input(colored("Nhấn Enter để tiếp tục nếu bạn đồng ý...", 'yellow'))
    
    consumed = 0
    try:
        while consumed < limit_gb:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("1.1.1.1", 80))  # Kết nối tới Cloudflare
                s.sendall(b"A" * 4096)
                consumed += 0.001  # Giả lập dữ liệu tiêu tốn
                print(colored(f"Đã tiêu tốn: {consumed:.2f} GB", 'green'), end="\r")
    except Exception as e:
        print(colored(f"Lỗi khi tiêu tốn dữ liệu: {e}", 'red'))
    print(colored("\nHoàn thành tiêu tốn dữ liệu!", 'green'))
    log_message(f"Data consumption completed: {consumed:.2f} GB used.")

# Tiêu tốn dữ liệu Wi-Fi
def consume_wifi_data(limit_gb=100):
    print(colored("\n=== Tiêu tốn dữ liệu Wi-Fi ===", 'yellow'))
    print(colored("CẢNH BÁO: Tiêu tốn dữ liệu Wi-Fi có thể làm giảm hiệu suất mạng!", 'red'))
    input(colored("Nhấn Enter để tiếp tục nếu bạn đồng ý...", 'yellow'))
    
    consumed = 0
    try:
        while consumed < limit_gb:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("1.1.1.1", 80))  # Kết nối tới Cloudflare (hoặc một máy chủ bất kỳ)
                s.sendall(b"A" * 4096)  # Gửi dữ liệu
                consumed += 0.001  # Giả lập dữ liệu tiêu tốn
                print(colored(f"Đã tiêu tốn: {consumed:.2f} GB", 'green'), end="\r")
    except Exception as e:
        print(colored(f"Lỗi khi tiêu tốn dữ liệu Wi-Fi: {e}", 'red'))
    print(colored("\nHoàn thành tiêu tốn dữ liệu Wi-Fi!", 'green'))
    log_message(f"Wi-Fi data consumption completed: {consumed:.2f} GB used.")

# Menu chính
def main():
    display_logo()
    display_warning()
    while True:
        print(colored("\n=== Menu Chính ===", 'cyan'))
        print("1. Kiểm tra tốc độ mạng")
        print("2. Quét thiết bị trong mạng LAN")
        print("3. Kiểm tra chịu tải mạng (Stress Test)")
        print("4. Kiểm tra băng thông (Bandwidth Saturation)")
        print("5. Tiêu tốn dữ liệu 4G")
        print("6. Tiêu tốn dữ liệu Wi-Fi")
        print("7. Thoát")
        mode = input("Chọn chức năng (1-7): ").strip()

        if mode == "1":
            test_speed()
        elif mode == "2":
            scan_network()
        elif mode == "3":
            target = input("Nhập địa chỉ IP mục tiêu (mặc định: 192.168.1.1): ").strip() or "192.168.1.1"
            duration = int(input("Nhập thời gian kiểm tra (giây, mặc định: 30): ").strip() or 30)
            connections = int(input("Nhập số kết nối cùng lúc (mặc định: 100): ").strip() or 100)
            protocol = input("Chọn giao thức (TCP/UDP, mặc định: TCP): ").strip() or "TCP"
            stress_test(target, duration, connections, protocol)
        elif mode == "4":
            target = input("Nhập địa chỉ IP mục tiêu (mặc định: 192.168.1.1): ").strip() or "192.168.1.1"
            duration = int(input("Nhập thời gian kiểm tra (giây, mặc định: 30): ").strip() or 30)
            bandwidth_saturation(target, duration)
        elif mode == "5":
            limit_gb = float(input("Nhập giới hạn dữ liệu tiêu tốn (GB, mặc định: 100): ").strip() or 100)
            consume_4g_data(limit_gb)
        elif mode == "6":
            limit_gb = float(input("Nhập giới hạn dữ liệu Wi-Fi tiêu tốn (GB, mặc định: 100): ").strip() or 100)
            consume_wifi_data(limit_gb)
        elif mode == "7":
            print(colored("Thoát khỏi chương trình.", 'cyan'))
            break
        else:
            print(colored("Lựa chọn không hợp lệ!", 'red'))

if __name__ == "__main__":
    main()