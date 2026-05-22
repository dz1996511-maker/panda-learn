"""
AI 学习助手 — 桌面启动器（端口 5000 固定）
先杀旧进程 → 启动服务 → 打开 Chrome 无边框窗口
"""

import subprocess
import sys
import os
import time
import threading
import logging
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 5000
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "data", "app.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")

def open_app():
    import urllib.request
    import webbrowser

    url = f"http://127.0.0.1:{PORT}"
    for _ in range(30):
        try:
            urllib.request.urlopen(url)
            break
        except Exception:
            time.sleep(0.5)

    # Chrome app mode
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for chrome in chrome_paths:
        if os.path.exists(chrome):
            subprocess.Popen([chrome, f"--app={url}", "--window-size=1280,800"])
            return
    webbrowser.open(url)

if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    logging.info(f"Starting on port {PORT}")

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    open_app()
    server_thread.join()
