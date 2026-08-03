# 🚀 5 分钟快速上手

## 方式 A：直接下载成品（推荐）

1. 进 [Releases](../../releases) 页面
2. 下载对应平台的文件：
   - **Windows** → `喵提醒中转.exe`
   - **Android** → `miaoremind-debug.apk`
3. 跳过下面的编译步骤，直接看「配置推送」

---

## 方式 B：自己编译（全自动）

### 前提
- 一个 GitHub 账号（免费）
- 什么都不用装！

### 步骤
1. **Fork 本仓库**（右上角 Fork 按钮）
2. **改代码**（可选）：在 `windows/main.py` 或 `apk/main.py` 里改你想改的
3. **打 Tag**：
   ```
   git tag v1.0.0
   git push origin v1.0.0
   ```
   或去 Actions 页面手动点 `Run workflow`
4. **等 20 分钟** → Releases 页面出现成品 ✅

---

## ⚙️ 配置推送渠道

下载运行后，编辑配置文件填入 Token：

| 渠道 | 获取地址 | 填写字段 |
|------|---------|---------|
| PushPlus | www.pushplus.plus | pushplus_token |
| Server酱 | sct.ftqq.com | serverchan_key |
| Bark | bark.day.app | bark_url |
| Telegram | @BotFather | telegram_bot_token + chat_id |
| 钉钉 | 钉钉群机器人 | dingtalk_webhook |

> 至少填一个，全空的话提醒只会在本地弹窗。

---

## 🐛 常见问题

**Q: Windows 被杀毒拦截？**
A: PyInstaller 的通病，加白名单即可。源码完全开源可审计。

**Q: Android 收不到通知？**
A: 检查「电池优化」是否允许后台运行，通知权限是否开启。

**Q: APK 编译失败？**
A: 看 Actions 日志最后 50 行，通常是依赖版本问题，提 Issue 我帮你看。
