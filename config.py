# 配置文件 - 全局常量和配置管理

import os
import json

# ========== 核心视觉优化：全局配色 ==========
WINDOW_BG = (1.0, 1.0, 1.0, 1)          # 窗口背景：纯白
INFO_TEXT_COLOR = (0.0, 0.3, 0.6, 1)    # 顶部信息：深蓝
QUESTION_BG = (0.05, 0.4, 0.8, 1)       # 题目背景：纯深蓝
QUESTION_TEXT_COLOR = (1.0, 1.0, 1.0, 1)# 题目文字：纯白
ANSWER_TEXT_COLOR = (0.0, 0.2, 0.7, 1)  # 答案文字：深蓝加粗
BUTTON_NORMAL_BG = (0.1, 0.6, 0.9, 1)   # 数字按钮：浅蓝
BUTTON_ACTION_BG = (0.0, 0.4, 0.8, 1)   # 清除/提交：深蓝
BUTTON_TEXT_COLOR = (1.0, 1.0, 1.0, 1)  # 按钮文字：纯白
TIP_TEXT_COLOR = (0.9, 0.1, 0.1, 1)     # 提示文字：红色

# 适配手机尺寸 + 纯白背景
WINDOW_SIZE = (400, 700)

# 全局常量
SAVE_FILE = "math_lock_save.json"
CONFIG_FILE = "math_lock_config.json"
DEFAULT_PWD = "8888"
FORGOT_PWD_HINT = "孩子的小名是什么？"
FORGOT_PWD_ANSWER = "宝贝"
ROUND_MAX = 5
PER_ROUND_UNLOCK_MIN = 30
FREE_PASS_ROUND = 3
NEED_CONTINUE_ROUND = 2
PER_ROUND_NEED_PASS = 10

# 加载配置文件
def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_default_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "per_round_need_pass": PER_ROUND_NEED_PASS,
            "parent_pwd": DEFAULT_PWD,
            "forgot_pwd_hint": FORGOT_PWD_HINT,
            "forgot_pwd_answer": FORGOT_PWD_ANSWER
        }

def save_default_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "per_round_need_pass": PER_ROUND_NEED_PASS,
            "parent_pwd": DEFAULT_PWD,
            "forgot_pwd_hint": FORGOT_PWD_HINT,
            "forgot_pwd_answer": FORGOT_PWD_ANSWER
        }, f, ensure_ascii=False)

config = load_config()

def get_parent_pwd():
    return config.get("parent_pwd", DEFAULT_PWD)

def get_forgot_pwd_hint():
    return config.get("forgot_pwd_hint", FORGOT_PWD_HINT)

def get_forgot_pwd_answer():
    return config.get("forgot_pwd_answer", FORGOT_PWD_ANSWER)