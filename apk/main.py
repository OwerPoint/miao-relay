#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
喵提醒中转 - Android 版 (Kivy)
监听本地端口 → 拦截请求 → 推送通知
"""

import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.scrollview import ScrollView
    from kivy.clock import Clock
    from kivy import Logger
except ImportError:
    # 非 Android 环境也能跑 server 部分
    pass

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
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

# ========== 推送 ==========
def push_all(title, content):
    cfg = load_config()
    results = []

    if cfg.get("pushplus_token"):
        try:
            import urllib.request
            url = f"http://www.pushplus.plus/send?token={cfg['pushplus_token']}&title={title}&content={content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("PushPlus ✅")
        except Exception as e:
            results.append(f"PushPlus ❌ {e}")

    if cfg.get("serverchan_key"):
        try:
            import urllib.request
            url = f"https://sctapi.ftqq.com/{cfg['serverchan_key']}.send?title={title}&desp={content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("Server酱 ✅")
        except Exception as e:
            results.append(f"Server酱 ❌ {e}")

    if cfg.get("bark_url"):
        try:
            import urllib.request
            url = f"{cfg['bark_url']}/{title}/{content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("Bark ✅")
        except Exception as e:
            results.append(f"Bark ❌ {e}")

    if cfg.get("telegram_bot_token") and cfg.get("telegram_chat_id"):
        try:
            import urllib.request
            url = f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/sendMessage?chat_id={cfg['telegram_chat_id']}&text={title}: {content}"
            urllib.request.urlopen(url, timeout=5)
            results.append("Telegram ✅")
        except Exception as e:
            results.append(f"Telegram ❌ {e}")

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

    # 本地通知
    try:
        from plyer import notification
        notification.notify(title=title, message=content, app_name="喵提醒中转")
    except:
        pass

    return results

# ========== HTTP 中转 ==========
class RelayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def _handle(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        title = params.get("title", ["喵提醒"])[0]
        content = params.get("content", params.get("text", ["新提醒"]))[0]

        results = push_all(title, content)

        resp = json.dumps({"status": "ok", "results": results}, ensure_ascii=False)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(resp.encode("utf-8"))

    def log_message(self, format, *args):
        pass

def start_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), RelayHandler)
    Logger.info(f"🐱 喵提醒中转已启动，端口 {port}")
    server.serve_forever()

# ========== Kivy UI ==========
class RelayApp(App):
    def build(self):
        self.cfg = load_config()
        self.title = "喵提醒中转 🐱"

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(
            text="🐱 喵提醒中转",
            font_size="24sp",
            size_hint_y=None,
            height="50dp"
        ))

        self.log_view = Label(
            text="服务未启动\n点击下方按钮启动",
            font_size="16sp",
            halign="left",
            valign="top",
            text_size=(400, None),
            size_hint_y=1
        )
        scroll = ScrollView()
        scroll.add_widget(self.log_view)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint_y=None, height="50dp", spacing=10)

        start_btn = Button(text="▶ 启动服务")
        start_btn.bind(on_press=self.on_start)
        btn_layout.add_widget(start_btn)

        config_btn = Button(text="⚙ 配置")
        config_btn.bind(on_press=self.on_config)
        btn_layout.add_widget(config_btn)

        layout.add_widget(btn_layout)
        return layout

    def on_start(self, instance):
        port = self.cfg.get("listen_port", 8080)
        t = threading.Thread(target=start_server, args=(port,), daemon=True)
        t.start()
        self.log_view.text = f"✅ 服务已启动\n监听端口: {port}\n\n等待喵提醒请求..."

    def on_config(self, instance):
        msg = "请编辑配置文件:\n" + CONFIG_PATH + "\n\n"
        msg += "支持的推送渠道:\n"
        msg += "- pushplus_token\n"
        msg += "- serverchan_key\n"
        msg += "- bark_url\n"
        msg += "- telegram_bot_token + chat_id\n"
        msg += "- dingtalk_webhook"
        self.log_view.text = msg

# ========== 入口 ==========
if __name__ == "__main__":
    try:
        RelayApp().run()
    except:
        # 无 Kivy 环境，跑命令行
        cfg = load_config()
        port = cfg.get("listen_port", 8080)
        print(f"🐱 喵提醒中转启动，端口 {port}")
        start_server(port)
