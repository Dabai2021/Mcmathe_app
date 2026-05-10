[app]

# 应用标题
title = 宝贝数学启蒙

# 应用包名（必须唯一，推荐格式：com.作者.应用名）
package.name = baimuchen_math

# 应用域名（与包名组合成完整包名）
package.domain = com.baimuchen

# 源码目录
source.dir = .

# 应用版本
version = 1.0

# 需要包含的Python模块（不含.py后缀）
requirements = python3,kivy

# 屏幕方向：'vertical'（竖屏）或 'horizontal'（横屏）
orientation = portrait

# 是否全屏
fullscreen = 0

# Android特定配置
android.permissions = INTERNET

# Android API版本（建议使用24或更高）
android.minapi = 24

# Android API目标版本
android.api = 28

# 是否支持arch arm64-v8a
android.archs = arm64-v8a, armeabi-v7a

# 是否支持arch x86_64（用于模拟器）
p4a.bootstrap = sdl2

# 是否启用androidx
android.enable_androidx = True

# 是否使用 PRIVATE_STORAGE（Android 10+需要）
android.allow_backup = True

# 是否启用无损压缩
android.numpy = False

# 窗口图标（PNG格式，48x48）
# icon.filename = icon.png

# 启动图片（PNG格式）
# splash.filename = splash.png

# 禁止打包这些文件
unzip_archive_patterns = *.pyc, *.pyo, *.pyd, .git, .svn, .hg, .DS_Store, Thumbs.db

# 是否打印详细日志
log_level = 2

# 是否启用调试模式
debug = 0

[buildozer]

# Buildozer版本
buildozer.version = 1.5.0

# 是否在打包前清理
build_dir = ./.buildozer

# Android SDK路径（如果不在默认位置）
# android.sdk_path = /path/to/android/sdk

# Android NDK路径（如果不在默认位置）
# android.ndk_path = /path/to/android/ndk

# Python For Android路径（如果不在默认位置）
# p4a.path = /path/to/python-for-android

# 是否使用virtualenv
use_virtualenv = True

# virtualenv路径
# virtualenv_dir = ./.venv