# 🐱 喵提醒中转

> 拦截 miaotixing.com 请求 → 转发到自有推送渠道（PushPlus / Server酱 / Bark / Telegram / 钉钉）

## ✨ 功能

- ✅ 劫持 `miaotixing.com` → 本地中转
- ✅ 6 大推送渠道支持
- ✅ Windows 系统托盘 + 一键安装/卸载 hosts
- ✅ Android 前台服务 + 通知栏
- ✅ GitHub Actions 全自动打包 EXE + APK

## 🚀 快速开始

### Windows
1. 下载 `喵提醒中转.exe`
2. 双击运行（会自动请求管理员权限写 hosts）
3. 编辑同目录 `_config.json`，填入你的推送 Token
4. 重启程序，搞定！

### Android
1. 下载 `miaoremind-debug.apk`
2. 安装并授予「通知」+「后台运行」权限
3. 打开 App → 点 ▶ 启动服务
4. 编辑配置填入推送 Token

## 🔧 配置说明

编辑 `_config.json`（Windows）或 App 内配置：

```json
{
    "pushplus_token": "你的PushPlus Token",
    "serverchan_key": "你的Server酱Key",
    "bark_url": "https://api.day.app/你的BarkKey",
    "telegram_bot_token": "123:ABC",
    "telegram_chat_id": "123456",
    "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
    "listen_port": 8080
}
```

至少填一个渠道即可。

## 📦 自动打包

每次打 Tag 自动触发 GitHub Actions：
```bash
git tag v1.0.0
git push origin v1.0.0
```

或去 Actions 页面手动点 `Run workflow`。

## 📜 License

MIT
