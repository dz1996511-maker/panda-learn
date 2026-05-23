"""
AI 学习助手 — 桌面启动器
端口 5000 固定，启动前自动清理旧进程
"""

import subprocess
import sys
import os
import time
import threading
import logging
import socket
import urllib.request
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 5000
URL = f"http://127.0.0.1:{PORT}"
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
logging.basicConfig(
    filename=os.path.join(BASE_DIR, "data", "app.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def kill_port(port):
    """杀掉占用端口的进程（Windows）"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) > 4 and parts[3] == "LISTENING":
                pid = parts[4]
                subprocess.run(f"taskkill /F /PID {pid} 2>nul", shell=True)
    except Exception:
        pass


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(('127.0.0.1', port)) == 0


def wait_for_server(max_retries=30, interval=0.5):
    for i in range(max_retries):
        try:
            urllib.request.urlopen(f"{URL}/api/check-api-key", timeout=2)
            return True
        except Exception:
            time.sleep(interval)
    return False


def start_server():
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


def open_browser():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for chrome in chrome_paths:
        if os.path.exists(chrome):
            subprocess.Popen([chrome, f"--app={URL}", "--window-size=1280,800"])
            return
    webbrowser.open(URL)


if __name__ == "__main__":
    print(f"🐼 熊猫学习助手 — 端口 {PORT}")
    print(f"   正在清理旧进程...")
    kill_port(PORT)
    time.sleep(0.5)

    print(f"   正在启动服务...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    if wait_for_server():
        print(f"   ✅ 服务就绪 {URL}")
        open_browser()
        print(f"   按 Ctrl+C 退出")
    else:
        print(f"   ❌ 服务启动失败，查看 data/app.log")
        sys.exit(1)

    try:
        server_thread.join()
    except KeyboardInterrupt:
        print(f"\n   正在关闭...")
        os._exit(0)
