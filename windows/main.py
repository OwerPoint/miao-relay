#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
喵提醒中转 - Windows 版
拦截 miaotixing.com 请求 → 转发到自有推送渠道
"""

import os
import sys
import json
import socket
import threading
import subprocess
import ctypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ========== 配置 ==========
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_config.json")
DEFAULT_CONFIG = {
    "pushplus_token": "",
    "serverchan_key": "",
    "bark_url": "",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "dingtalk_webhook": "",
    "listen_port": 8080,
    "forward_target": "https://miaotixing.com"
}

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
HOSTS_MARKER_BEGIN = "# >>> 喵提醒中转 BEGIN >>>"
HOSTS_MARKER_END = "# <<< 喵提醒中转 END <<<"

# ========== 工具函数 ==========
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# ========== Hosts 管理 ==========
def install_hosts():
    """写入 hosts 劫持规则"""
    entry = f"127.0.0.1 miaotixing.com\n127.0.0.1 www.miaotixing.com"
    block = f"\n{HOSTS_MARKER_BEGIN}\n{entry}\n{HOSTS_MARKER_END}\n"

    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(HOSTS_PATH, "r", encoding="gbk") as f:
            content = f.read()

    if HOSTS_MARKER_BEGIN in content:
        return "hosts 已存在劫持规则，无需重复安装"

    with open(HOSTS_PATH, "a", encoding="utf-8") as f:
        f.write(block)

    flush_dns()
    return "✅ hosts 劫持规则已写入"

def uninstall_hosts():
    """移除 hosts 劫持规则"""
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(HOSTS_PATH, "r", encoding="gbk") as f:
            lines = f.readlines()

    new_lines = []
    skip = False
    for line in lines:
        if HOSTS_MARKER_BEGIN in line:
            skip = True
            continue
        if HOSTS_MARKER_END in line:
            skip = False
            continue
        if not skip:
            new_lines.append(line)

    with open(HOSTS_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    flush_dns()
    return "✅ hosts 劫持规则已移除"

def flush_dns():
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=10)
    except:
        pass

# ========== 推送渠道 ==========
def push_all(title, content):
    """向所有已配置的渠道推送"""
    cfg = load_config()
    results = []

    # PushPlus
    if cfg.get("pushplus_token"):
        try:
            import urllib.request
            url = f"http://www.pushplus.plus/send?token={cfg['pushplus_token']}&title={title}&content={content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("PushPlus ✅")
        except Exception as e:
            results.append(f"PushPlus ❌ {e}")

    # Server酱
    if cfg.get("serverchan_key"):
        try:
            import urllib.request
            url = f"https://sctapi.ftqq.com/{cfg['serverchan_key']}.send?title={title}&desp={content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("Server酱 ✅")
        except Exception as e:
            results.append(f"Server酱 ❌ {e}")

    # Bark
    if cfg.get("bark_url"):
        try:
            import urllib.request
            url = f"{cfg['bark_url']}/{title}/{content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("Bark ✅")
        except Exception as e:
            results.append(f"Bark ❌ {e}")

    # Telegram
    if cfg.get("telegram_bot_token") and cfg.get("telegram_chat_id"):
        try:
            import urllib.request
            url = f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/sendMessage?chat_id={cfg['telegram_chat_id']}&text={title}: {content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("Telegram ✅")
        except Exception as e:
            results.append(f"Telegram ❌ {e}")

    # 钉钉
    if cfg.get("dingtalk_webhook"):
        try:
            import json as json_mod
            import urllib.request
            data = json_mod.dumps({
                "msgtype": "text",
                "text": {"content": f"{title}: {content}"}
            }).encode("utf-8")
            req = urllib.request.Request(cfg["dingtalk_webhook"], data=data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            results.append("钉钉 ✅")
        except Exception as e:
            results.append(f"钉钉 ❌ {e}")

    return results

# ========== HTTP 中转服务器 ==========
class RelayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def _handle(self):
        cfg = load_config()
        port = cfg.get("listen_port", 8080)

        # 解析请求
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # 提取参数
        title = params.get("title", ["喵提醒"])[0]
        content = params.get("content", params.get("text", ["新提醒"]))[0]

        # 推送
        results = push_all(title, content)

        # 返回响应
        resp = json.dumps({
            "status": "ok",
            "message": "已转发推送",
            "results": results
        }, ensure_ascii=False)

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(resp.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # 静默日志

def start_server():
    cfg = load_config()
    port = cfg.get("listen_port", 8080)
    server = HTTPServer(("0.0.0.0", port), RelayHandler)
    print(f"🐱 喵提醒中转已启动，监听端口 {port}")
    server.serve_forever()

# ========== 系统托盘 ==========
def start_tray():
    """启动系统托盘（如果有 pystray）"""
    try:
        import pystray
        from PIL import Image, ImageDraw

        cfg = load_config()

        # 创建图标
        img = Image.new("RGB", (64, 64), color=(255, 165, 0))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "🐱", fill=(255, 255, 255))

        def on_install():
            msg = install_hosts()
            show_notification("喵提醒中转", msg)

        def on_uninstall():
            msg = uninstall_hosts()
            show_notification("喵提醒中转", msg)

        def on_config():
            show_notification("配置", f"编辑 {CONFIG_PATH} 后重启程序")

        def on_quit():
            uninstall_hosts()
            icon.stop()

        icon = pystray.Icon(
            "喵提醒中转",
            img,
            "喵提醒中转 🐱",
            menu=pystray.Menu(
                pystray.MenuItem("安装 hosts 劫持", on_install),
                pystray.MenuItem("移除 hosts 劫持", on_uninstall),
                pystray.MenuItem("查看配置路径", on_config),
                pystray.MenuItem("退出并清理", on_quit),
            )
        )
        icon.run()
    except ImportError:
        # 没有 pystray 就跑命令行模式
        run_cli()

def show_notification(title, message):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name="喵提醒中转")
    except:
        print(f"[{title}] {message}")

# ========== 命令行模式 ==========
def run_cli():
    print("=" * 50)
    print("🐱 喵提醒中转 v1.0.0")
    print("=" * 50)
    print("1. 安装 hosts 劫持")
    print("2. 移除 hosts 劫持")
    print("3. 启动中转服务")
    print("4. 退出")
    print("-" * 50)

    while True:
        choice = input("选择操作 [1-4]: ").strip()
        if choice == "1":
            print(install_hosts())
        elif choice == "2":
            print(uninstall_hosts())
        elif choice == "3":
            print("🚀 中转服务启动中... (Ctrl+C 停止)")
            try:
                start_server()
            except KeyboardInterrupt:
                print("\n⏹️ 服务已停止")
        elif choice == "4":
            break
        else:
            print("无效选择")

# ========== 入口 ==========
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == "install":
            print(install_hosts())
        elif sys.argv[1] == "uninstall":
            print(uninstall_hosts())
        elif sys.argv[1] == "serve":
            start_server()
        else:
            run_cli()
    else:
        # 默认：尝试托盘，失败则命令行
        if is_admin():
            start_tray()
        else:
            run_cli()
