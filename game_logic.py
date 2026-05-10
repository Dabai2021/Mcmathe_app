# 游戏逻辑模块

import random
from datetime import datetime
from config import SAVE_FILE, PER_ROUND_NEED_PASS, ROUND_MAX
from question_types import create_question, QuestionTypeRegistry

class GameState:
    def __init__(self):
        self.level = 1
        self.max_level = 60
        self.correct_count = 0
        self.total_questions = 0
        self.max_questions_per_level = 5
        self.level_pass_rate = 1.0
        self.level_config = self.init_level_config()
        
        # 当前题目
        self.num1 = 0
        self.num2 = 0
        self.current_op = ""
        self.current_answer = 0
        self.user_answer_text = ""
        
        # 管控业务数据
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        self.daily_round = 0
        self.total_pass_today = 0
        self.last_stop_level = 1
        self.is_locked_today = False
        self.unlock_remain_sec = 0
        self.per_round_need_pass = PER_ROUND_NEED_PASS
        
        # UI引用
        self.info_label = None
        self.tip_label = None
        self.progress = None
        self.question_label = None
        self.answer_show = None

    def init_level_config(self):
        """
        关卡难度梯度设计
        前三轮：
        1-5关：十以内加法
        5-10关：十以内减法
        10-15关：二十以内加法
        15-20关：二十以内加减混合
        20-25关：初识乘法（10以内）
        25-30关：初识除法（10以内）
        30-40关：乘法表进阶（12以内）
        40-50关：除法进阶（12以内）
        50-60关：四则混合运算
        
        第四轮及以后：
        1-10关：20以内加减混合
        10-20关：12以内乘除混合
        20-60关：20以内四则混合
        """
        config = {}
        for i in range(1, 61):
            if i <= 5:
                # 1-5关：十以内加法
                config[i] = {
                    "max_num": 10,
                    "operations": ["addition"],
                    "difficulty": "简单",
                    "description": "10以内加法"
                }
            elif i <= 10:
                # 5-10关：十以内减法
                config[i] = {
                    "max_num": 10,
                    "operations": ["subtraction"],
                    "difficulty": "简单",
                    "description": "10以内减法"
                }
            elif i <= 15:
                # 10-15关：二十以内加法
                config[i] = {
                    "max_num": 20,
                    "operations": ["addition"],
                    "difficulty": "中等",
                    "description": "20以内加法"
                }
            elif i <= 20:
                # 15-20关：二十以内加减混合
                config[i] = {
                    "max_num": 20,
                    "operations": ["addition", "subtraction"],
                    "difficulty": "中等",
                    "description": "20以内加减"
                }
            elif i <= 25:
                # 20-25关：初识乘法（10以内）
                config[i] = {
                    "max_num": 10,
                    "operations": ["multiplication"],
                    "difficulty": "中等",
                    "description": "10以内乘法"
                }
            elif i <= 30:
                # 25-30关：初识除法（10以内）
                config[i] = {
                    "max_num": 10,
                    "operations": ["division"],
                    "difficulty": "中等",
                    "description": "10以内除法"
                }
            elif i <= 40:
                # 30-40关：乘法表进阶（12以内）
                config[i] = {
                    "max_num": 12,
                    "operations": ["multiplication"],
                    "difficulty": "较难",
                    "description": "乘除法进阶"
                }
            elif i <= 50:
                # 40-50关：除法进阶（12以内）
                config[i] = {
                    "max_num": 12,
                    "operations": ["multiplication", "division"],
                    "difficulty": "较难",
                    "description": "乘除法混合"
                }
            elif i <= 60:
                # 50-60关：四则混合运算
                config[i] = {
                    "max_num": 20,
                    "operations": ["addition", "subtraction", "multiplication", "division"],
                    "difficulty": "困难",
                    "description": "四则混合运算"
                }
        return config
    
    def get_level_config(self):
        """
        获取当前关卡配置
        第四轮及以后难度提升
        """
        if self.daily_round >= 3:  # 第四轮开始（索引从0开始）
            config = {}
            for i in range(1, 61):
                if i <= 10:
                    # 1-10关：20以内加减混合
                    config[i] = {
                        "max_num": 20,
                        "operations": ["addition", "subtraction"],
                        "difficulty": "中等",
                        "description": "20以内加减混合"
                    }
                elif i <= 20:
                    # 10-20关：12以内乘除混合
                    config[i] = {
                        "max_num": 12,
                        "operations": ["multiplication", "division"],
                        "difficulty": "较难",
                        "description": "12以内乘除混合"
                    }
                else:
                    # 20-60关：20以内四则混合
                    config[i] = {
                        "max_num": 20,
                        "operations": ["addition", "subtraction", "multiplication", "division"],
                        "difficulty": "困难",
                        "description": "20以内四则混合"
                    }
            return config.get(self.level, {"max_num": 20, "operations": ["addition", "subtraction", "multiplication", "division"]})
        else:
            return self.level_config.get(self.level, {"max_num": 10, "operations": ["addition"]})

    def generate_question(self):
        """
        使用模块化题目系统生成题目
        预留扩展接口，方便以后添加更高级的数学题目
        """
        level_info = self.get_level_config()
        max_num = level_info["max_num"]
        operations = level_info["operations"]
        op_type = random.choice(operations)
        
        try:
            # 使用模块化题目系统
            question_text, answer = create_question(op_type, max_num)
            self.current_answer = answer
            
            # 解析题目文本获取数字和运算符（用于显示）
            parts = question_text.replace(" = ?", "").split()
            if len(parts) >= 3:
                self.num1 = int(parts[0])
                self.current_op = parts[1]
                self.num2 = int(parts[2])
            
            return question_text
        except Exception as e:
            # 备用方案：如果题目系统出现问题，使用简单的生成方式
            print(f"题目生成错误: {e}")
            if op_type == "addition":
                self.num1 = random.randint(1, max_num)
                self.num2 = random.randint(1, max_num - self.num1)
                self.current_answer = self.num1 + self.num2
                self.current_op = "+"
            elif op_type == "subtraction":
                self.num1 = random.randint(1, max_num)
                self.num2 = random.randint(0, min(self.num1, max_num))
                self.current_answer = self.num1 - self.num2
                self.current_op = "-"
            elif op_type == "multiplication":
                self.num1 = random.randint(1, min(max_num, 12))
                self.num2 = random.randint(1, min(max_num, 12))
                self.current_answer = self.num1 * self.num2
                self.current_op = "×"
            elif op_type == "division":
                self.num2 = random.randint(1, min(max_num, 12))
                self.current_answer = random.randint(1, min(max_num, 12))
                self.num1 = self.num2 * self.current_answer
                self.current_op = "÷"
            
            return f"{self.num1} {self.current_op} {self.num2} = ?"

    def check_answer(self, user_answer):
        try:
            user_ans = int(user_answer)
        except:
            return None, "请输入正确的数字！"
        
        self.total_questions += 1
        
        if user_ans == self.current_answer:
            self.correct_count += 1
            return True, "太棒了！答对了！🎉"
        else:
            return False, f"答案是 {self.current_answer}，继续加油！💪"

    def is_level_complete(self):
        return self.correct_count >= self.max_questions_per_level

    def reset_question(self):
        self.user_answer_text = ""

    def load_save_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("date") == self.today_str:
                        self.daily_round = data.get("daily_round", 0)
                        self.last_stop_level = data.get("last_stop_level", 1)
                        self.total_pass_today = data.get("total_pass_today", 0)
                        self.per_round_need_pass = data.get("per_round_need_pass", PER_ROUND_NEED_PASS)
            except:
                pass

    def save_save_data(self):
        save_data = {
            "date": self.today_str,
            "daily_round": self.daily_round,
            "last_stop_level": self.last_stop_level,
            "total_pass_today": self.total_pass_today,
            "per_round_need_pass": self.per_round_need_pass
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False)

    def reset_daily_if_need(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("date") != self.today_str:
                        self.daily_round = 0
                        self.total_pass_today = 0
                        self.is_locked_today = False
            except:
                pass

import os
import json