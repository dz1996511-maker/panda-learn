"""
AI 学习助手 — 桌面启动器
启动服务并在 Chrome App 模式中打开（无边框桌面窗口）
支持 pythonw.exe 无控制台窗口运行
"""

import subprocess
import sys
import os
import time
import threading
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "data", "app.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def start_server():
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="warning")


def open_app():
    import urllib.request
    import webbrowser

    for i in range(30):
        try:
            urllib.request.urlopen("http://127.0.0.1:5000/")
            break
        except Exception:
            time.sleep(0.5)

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]

    for chrome in chrome_paths:
        if os.path.exists(chrome):
            subprocess.Popen([
                chrome,
                "--app=http://127.0.0.1:8000",
                "--window-size=1280,800",
            ])
            return

    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    logging.info("AI 学习助手 启动中...")
    # 确保 data 目录存在
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    open_app()
    server_thread.join()
