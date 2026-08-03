[app]
title = 喵提醒中转
package.name = miaoremind
package.domain = org.example.miaoremind
source.dir = .
source.main = main.py
source.include_exts = py,kv,json,txt,png,jpg
version = 1.0.0
orientation = portrait

# 依赖：锁定版本避免编译错误
requirements = python3,kivy==2.2.1,cython==0.29.36,plyer,requests

# 启动图和图标（留空 = 默认）
presplash.filename =
icon.filename =

# Android 权限
android.permissions = INTERNET,VIBRATE,FOREGROUND_SERVICE,POST_NOTIFICATIONS,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.add_locales = zh_CN,en_US
android.enable_androidx = True

# 编译选项
android.archs = arm64-v8a,armeabi-v7a
android.release = False

[buildozer]
log_level = 2
warn_on_root = 1
