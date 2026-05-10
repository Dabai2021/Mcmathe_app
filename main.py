# 宝贝数学启蒙APP 完整版
# 主入口文件

import os
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

import logging
logging.getLogger('kivy').setLevel(logging.WARNING)
logging.getLogger('comtypes').setLevel(logging.WARNING)
logging.getLogger('comtypes.client').setLevel(logging.WARNING)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle, Line
import pyttsx3
import json
from datetime import datetime

from config import *
from game_logic import GameState

# 注册系统微软雅黑
LabelBase.register(name='MicrosoftYaHei',
                   fn_regular='C:/Windows/Fonts/msyh.ttc')

# 设置窗口
Window.size = WINDOW_SIZE
Window.clearcolor = WINDOW_BG

class MathLockApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # 游戏状态
        self.game_state = GameState()
        self.level_config = self.game_state.init_level_config()
        
        # UI引用
        self.info_label = None
        self.tip_label = None
        self.progress = None
        self.question_label = None
        self.answer_show = None
        
        # 设置弹窗实例
        self.setting_popup = None
        
        # 加载存档和配置
        self.game_state.load_save_data()
        self.game_state.reset_daily_if_need()
        self.per_round_need_pass = self.game_state.per_round_need_pass
        
        # 初始化语音引擎（仅PC端）
        self.tts_engine = None
        if not IS_ANDROID:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 1.0)
                
                voices = self.tts_engine.getProperty('voices')
                chinese_voice = None
                for voice in voices:
                    voice_langs = voice.languages if voice.languages else []
                    if any("zh" in str(lang).lower() for lang in voice_langs):
                        chinese_voice = voice.id
                        break
                    if hasattr(voice, 'name') and ('chinese' in voice.name.lower() or 'chinese' in str(voice).lower()):
                        chinese_voice = voice.id
                        break
                
                if chinese_voice:
                    self.tts_engine.setProperty('voice', chinese_voice)
            except Exception as e:
                print(f"语音引擎初始化失败: {e}")
                self.tts_engine = None
        
        # 标记答题UI是否已构建
        self.game_ui_built = False
        
        # 显示开始界面
        self.show_start_screen()
        
        # 定时检测凌晨重置
        Clock.schedule_interval(self.auto_daily_reset, 60)

    def show_start_screen(self):
        """显示开始选择界面"""
        self.clear_widgets()
        
        start_layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        # 标题
        title = Label(
            text='宝贝数学启蒙',
            font_size=40,
            font_name='MicrosoftYaHei',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=0.2
        )
        start_layout.add_widget(title)
        
        # 轮次信息
        round_info = Label(
            text=f'第 {self.game_state.daily_round + 1} 轮',
            font_size=28,
            font_name='MicrosoftYaHei',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.15
        )
        start_layout.add_widget(round_info)
        
        # 提示信息
        if self.game_state.daily_round >= 3:
            # 第四轮及以后：强制接续
            prompt_label = Label(
                text=f'第{self.game_state.daily_round + 1}轮开始，继续挑战！',
                font_size=24,
                font_name='MicrosoftYaHei',
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=0.15
            )
            start_layout.add_widget(prompt_label)
            
            # 只显示开始按钮
            btn_layout = BoxLayout(orientation='vertical', size_hint_y=0.35)
            
            start_btn = Button(
                text=f'从第{self.game_state.last_stop_level}关开始',
                font_size=32,
                font_name='MicrosoftYaHei',
                background_color=(0.2, 0.8, 0.2, 1),
                size_hint_y=0.5
            )
            btn_layout.add_widget(start_btn)
            
            def on_start(instance):
                self.game_state.level = self.game_state.last_stop_level
                self.build_game_ui()
                self.start_game()
            
            start_btn.bind(on_press=on_start)
            
            start_layout.add_widget(btn_layout)
        else:
            # 前三轮：可以选择
            if self.game_state.last_stop_level > 1:
                prompt_label = Label(
                    text=f'上次在第 {self.game_state.last_stop_level} 关结束',
                    font_size=24,
                    font_name='MicrosoftYaHei',
                    color=(0.4, 0.4, 0.4, 1),
                    size_hint_y=0.15
                )
            else:
                prompt_label = Label(
                    text='准备开始新的旅程！',
                    font_size=24,
                    font_name='MicrosoftYaHei',
                    color=(0.4, 0.4, 0.4, 1),
                    size_hint_y=0.15
                )
            start_layout.add_widget(prompt_label)
            
            # 按钮区域
            btn_layout = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=20)
            
            # 接续上次按钮（绿色）
            continue_btn = Button(
                text='接续上次',
                font_size=32,
                font_name='MicrosoftYaHei',
                background_color=(0.2, 0.8, 0.2, 1),
                size_hint_y=0.45
            )
            btn_layout.add_widget(continue_btn)
            
            def on_continue(instance):
                self.game_state.level = self.game_state.last_stop_level
                self.build_game_ui()
                self.start_game()
            
            continue_btn.bind(on_press=on_continue)
            
            # 从头开始按钮（红色）
            start_over_btn = Button(
                text='从头开始',
                font_size=32,
                font_name='MicrosoftYaHei',
                background_color=(0.9, 0.5, 0.5, 1),
                size_hint_y=0.45
            )
            btn_layout.add_widget(start_over_btn)
            
            def on_start_over(instance):
                self.game_state.level = 1
                self.game_state.last_stop_level = 1
                self.game_state.save_save_data()
                self.build_game_ui()
                self.start_game()
            
            start_over_btn.bind(on_press=on_start_over)
            
            start_layout.add_widget(btn_layout)
        
        self.add_widget(start_layout)

    def build_game_ui(self):
        """构建答题界面"""
        self.clear_widgets()
        self.game_ui_built = True
        
        # 顶部信息栏
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        
        self.info_label = Label(
            text=f"当前第{self.game_state.level}关 | 今日轮次：{self.game_state.daily_round}/{ROUND_MAX}",
            font_size=18,
            font_name='MicrosoftYaHei',
            color=INFO_TEXT_COLOR
        )
        info_layout.add_widget(self.info_label)
        
        self.setting_btn = Button(
            text='家长设置',
            font_size=18,
            font_name='MicrosoftYaHei',
            background_color=(0.8, 0.6, 0.4, 1),
            size_hint_x=0.3
        )
        self.setting_btn.bind(on_press=self.show_parent_setting)
        info_layout.add_widget(self.setting_btn)
        
        self.add_widget(info_layout)
        
        # 进度条
        self.progress = ProgressBar(max=100, value=0, size_hint_y=0.05)
        self.add_widget(self.progress)
        
        # 题目区域
        question_box = BoxLayout(orientation='vertical', size_hint_y=0.20)
        with question_box.canvas.before:
            Color(*QUESTION_BG)
            self.question_bg_rect = Rectangle(pos=question_box.pos, size=question_box.size)
        
        def update_question_bg_pos(instance, value):
            self.question_bg_rect.pos = value
        
        def update_question_bg_size(instance, value):
            self.question_bg_rect.size = value
        
        question_box.bind(pos=update_question_bg_pos)
        question_box.bind(size=update_question_bg_size)
        
        self.question_label = Label(
            text='',
            font_size=48,
            font_name='MicrosoftYaHei',
            color=QUESTION_TEXT_COLOR,
            bold=True
        )
        question_box.add_widget(self.question_label)
        
        self.add_widget(question_box)
        
        # 答案显示区域
        answer_box = BoxLayout(orientation='vertical', size_hint_y=0.10)
        with answer_box.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.answer_bg_rect = Rectangle(pos=answer_box.pos, size=answer_box.size)
        
        answer_box.bind(pos=lambda self, pos: setattr(self, 'canvas.before.children[1].pos', pos))
        answer_box.bind(size=lambda self, size: setattr(self, 'canvas.before.children[1].size', size))
        
        self.answer_show = Label(
            text='',
            font_size=36,
            font_name='MicrosoftYaHei',
            color=ANSWER_TEXT_COLOR,
            bold=True
        )
        answer_box.add_widget(self.answer_show)
        
        self.add_widget(answer_box)
        
        # 提示标签
        self.tip_label = Label(
            text='',
            font_size=20,
            font_name='MicrosoftYaHei',
            color=TIP_TEXT_COLOR,
            size_hint_y=0.05
        )
        self.add_widget(self.tip_label)
        
        # 数字键盘（适配手机操作）
        keypad_layout = GridLayout(cols=3, size_hint_y=0.48, spacing=10, padding=8, row_default_height=70)
        
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '清除', '0', '提交']
        for num in numbers:
            if num == '清除':
                btn = Button(
                    text=num,
                    font_size=32,
                    font_name='MicrosoftYaHei',
                    background_color=BUTTON_ACTION_BG,
                    color=BUTTON_TEXT_COLOR,
                    size_hint_y=None,
                    height=65
                )
                btn.bind(on_press=self.clear_answer)
            elif num == '提交':
                btn = Button(
                    text=num,
                    font_size=32,
                    font_name='MicrosoftYaHei',
                    background_color=(0.2, 0.8, 0.2, 1),
                    color=BUTTON_TEXT_COLOR,
                    size_hint_y=None,
                    height=65
                )
                btn.bind(on_press=self.check_ans)
            else:
                btn = Button(
                    text=num,
                    font_size=40,
                    font_name='MicrosoftYaHei',
                    background_color=BUTTON_NORMAL_BG,
                    color=BUTTON_TEXT_COLOR,
                    size_hint_y=None,
                    height=65
                )
                btn.bind(on_press=self.add_number)
            
            keypad_layout.add_widget(btn)
        
        self.add_widget(keypad_layout)

    def add_number(self, instance):
        self.game_state.user_answer_text += instance.text
        self.answer_show.text = self.game_state.user_answer_text
    
    def clear_answer(self, instance):
        self.game_state.user_answer_text = ''
        self.answer_show.text = ''
    
    def check_ans(self, instance):
        if not self.game_state.user_answer_text:
            self.tip_label.text = "请输入答案哦！"
            self.speak("请输入答案哦")
            return
        
        try:
            user_ans = int(self.game_state.user_answer_text)
        except:
            self.tip_label.text = "请输入正确的数字！"
            self.speak("请输入正确的数字")
            return
        
        self.game_state.total_questions += 1
        
        if user_ans == self.game_state.current_answer:
            self.game_state.correct_count += 1
            self.tip_label.text = "太棒了！答对了！🎉"
            self.speak("太棒了，答对了")
            self.update_progress()
            
            if self.game_state.correct_count >= self.game_state.max_questions_per_level:
                self.level_up()
            else:
                Clock.schedule_once(lambda dt: self.new_question(), 1.5)
        else:
            error_text = f"正确答案是 {self.game_state.current_answer}，继续加油！💪"
            self.tip_label.text = error_text
            print(f"宝贝你答错了： - {error_text}")
            
            def play_error_sound():
                try:
                    if self.tts_engine is not None:
                        self.tts_engine.stop()
                        self.tts_engine.say(f"答案是 {self.game_state.current_answer}，继续加油")
                        self.tts_engine.runAndWait()
                        print("语音播放完成")
                except Exception as e:
                    print(f"语音播放错误: {e}")
            
            Clock.schedule_once(lambda dt: play_error_sound(), 0.1)
            Clock.schedule_once(lambda dt: self.new_question(), 2.0)

    def update_progress(self):
        progress = (self.game_state.correct_count / self.game_state.max_questions_per_level) * 100
        self.progress.value = progress

    def level_up(self):
        self.game_state.last_stop_level = self.game_state.level
        self.game_state.level += 1
        self.game_state.total_pass_today += 1
        self.game_state.correct_count = 0
        self.game_state.total_questions = 0
        self.progress.value = 0
        
        self.game_state.save_save_data()
        
        if self.game_state.total_pass_today >= self.per_round_need_pass:
            self.game_state.daily_round += 1
            self.game_state.total_pass_today = 0
            self.tip_label.text = f"🎉 本轮完成！已通关 {self.per_round_need_pass} 关！"
            self.speak(f"本轮完成，已通关{self.per_round_need_pass}关")
            
            if self.game_state.daily_round >= ROUND_MAX:
                self.game_state.is_locked_today = True
                self.tip_label.text = "今日游戏次数已用完，请明天再来！"
                self.speak("今日游戏次数已用完，请明天再来")
            else:
                Clock.schedule_once(lambda dt: self.show_start_screen(), 3)
        else:
            if self.game_ui_built:
                level_info = self.game_state.get_level_config()
                self.info_label.text = f"第{self.game_state.level}关 - {level_info.get('description', '')} | 轮次：{self.game_state.daily_round}/{ROUND_MAX}"
            self.tip_label.text = f"恭喜通关！进入第{self.game_state.level}关 🎊"
            self.speak(f"恭喜通关，进入第{self.game_state.level}关")
            Clock.schedule_once(lambda dt: self.new_question(), 2)

    def new_question(self):
        question_text = self.game_state.generate_question()
        self.question_label.text = question_text
        self.game_state.user_answer_text = ''
        self.answer_show.text = ''
        self.tip_label.text = ''

    def speak(self, text):
        try:
            if self.tts_engine is None:
                return
            self.tts_engine.stop()
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"语音播放错误: {e}")

    def start_game(self):
        self.game_state.correct_count = 0
        self.game_state.total_questions = 0
        if self.game_ui_built:
            level_info = self.game_state.get_level_config()
            self.info_label.text = f"第{self.game_state.level}关 - {level_info.get('description', '')} | 轮次：{self.game_state.daily_round}/{ROUND_MAX}"
            self.new_question()
            self.speak("游戏已准备就绪，开始答题吧！")

    def show_parent_setting(self, instance):
        self.show_pwd_dialog()

    def show_pwd_dialog(self):
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        title = Label(
            text='请输入家长密码',
            font_size=24,
            font_name='MicrosoftYaHei',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=0.25
        )
        layout.add_widget(title)
        
        self.pwd_input = TextInput(
            multiline=False,
            password=True,
            font_size=24,
            font_name='MicrosoftYaHei',
            halign='center',
            size_hint_y=0.2
        )
        layout.add_widget(self.pwd_input)
        
        forgot_label = Label(
            text='忘记密码？',
            font_size=18,
            font_name='MicrosoftYaHei',
            color=(0.2, 0.5, 0.9, 1),
            size_hint_y=0.15
        )
        forgot_label.bind(on_touch_down=self.show_forgot_pwd)
        layout.add_widget(forgot_label)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
        
        cancel_btn = Button(
            text='取消',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        confirm_btn = Button(
            text='确认',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        layout.add_widget(btn_layout)
        
        self.pwd_popup = Popup(
            title='',
            content=layout,
            size_hint=(0.85, 0.5),
            background_color=(1, 1, 0.95, 1),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=self.on_pwd_cancel)
        confirm_btn.bind(on_press=self.on_pwd_confirm)
        
        self.pwd_popup.open()

    def on_pwd_cancel(self, instance):
        if self.pwd_popup:
            self.pwd_popup.dismiss()
            self.pwd_popup = None

    def on_pwd_confirm(self, instance):
        user_pwd = self.pwd_input.text.strip()
        if user_pwd == get_parent_pwd():
            if self.pwd_popup:
                self.pwd_popup.dismiss()
                self.pwd_popup = None
            self.show_setting_panel()
        else:
            self.tip_label.text = "密码错误，请重试！"
            self.pwd_input.text = ''

    def show_forgot_pwd(self, instance, touch):
        if instance.collide_point(*touch.pos):
            layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
            
            hint_label = Label(
                text=get_forgot_pwd_hint(),
                font_size=22,
                font_name='MicrosoftYaHei',
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=0.3
            )
            layout.add_widget(hint_label)
            
            forgot_input = TextInput(
                multiline=False,
                font_size=24,
                font_name='MicrosoftYaHei',
                halign='center',
                size_hint_y=0.2
            )
            layout.add_widget(forgot_input)
            
            btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
            
            cancel_btn = Button(
                text='取消',
                font_size=20,
                font_name='MicrosoftYaHei',
                background_color=(0.7, 0.7, 0.7, 1)
            )
            confirm_btn = Button(
                text='确认',
                font_size=20,
                font_name='MicrosoftYaHei',
                background_color=(0.2, 0.8, 0.2, 1)
            )
            
            btn_layout.add_widget(cancel_btn)
            btn_layout.add_widget(confirm_btn)
            layout.add_widget(btn_layout)
            
            forgot_popup = Popup(
                title='',
                content=layout,
                size_hint=(0.85, 0.45),
                background_color=(1, 1, 0.95, 1),
                auto_dismiss=False
            )
            
            def on_cancel(instance):
                forgot_popup.dismiss()
            
            def on_confirm(instance):
                if forgot_input.text.strip() == get_forgot_pwd_answer():
                    forgot_popup.dismiss()
                    self.show_pwd_reset()
                else:
                    self.tip_label.text = "答案错误，请重试！"
                    forgot_input.text = ''
            
            cancel_btn.bind(on_press=on_cancel)
            confirm_btn.bind(on_press=on_confirm)
            
            if self.pwd_popup:
                self.pwd_popup.dismiss()
            forgot_popup.open()

    def show_pwd_reset(self):
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        title = Label(
            text='重置密码',
            font_size=24,
            font_name='MicrosoftYaHei',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=0.2
        )
        layout.add_widget(title)
        
        new_pwd_label = Label(
            text='新密码：',
            font_size=20,
            font_name='MicrosoftYaHei',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.15
        )
        layout.add_widget(new_pwd_label)
        
        new_pwd_input = TextInput(
            multiline=False,
            password=True,
            font_size=24,
            font_name='MicrosoftYaHei',
            halign='center',
            size_hint_y=0.2
        )
        layout.add_widget(new_pwd_input)
        
        confirm_pwd_label = Label(
            text='确认密码：',
            font_size=20,
            font_name='MicrosoftYaHei',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.15
        )
        layout.add_widget(confirm_pwd_label)
        
        confirm_pwd_input = TextInput(
            multiline=False,
            password=True,
            font_size=24,
            font_name='MicrosoftYaHei',
            halign='center',
            size_hint_y=0.2
        )
        layout.add_widget(confirm_pwd_input)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
        
        cancel_btn = Button(
            text='取消',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        ok_btn = Button(
            text='确定',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(ok_btn)
        layout.add_widget(btn_layout)
        
        reset_popup = Popup(
            title='',
            content=layout,
            size_hint=(0.85, 0.6),
            background_color=(1, 1, 0.95, 1),
            auto_dismiss=False
        )
        
        def on_cancel(instance):
            reset_popup.dismiss()
            self.show_pwd_dialog()
        
        def on_ok(instance):
            new_pwd = new_pwd_input.text.strip()
            confirm_pwd = confirm_pwd_input.text.strip()
            
            if not new_pwd:
                self.tip_label.text = "请输入新密码！"
                return
            if new_pwd != confirm_pwd:
                self.tip_label.text = "两次输入的密码不一致！"
                return
            
            config["parent_pwd"] = new_pwd
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False)
            
            self.tip_label.text = "密码已重置成功！"
            reset_popup.dismiss()
            self.show_setting_panel()
        
        cancel_btn.bind(on_press=on_cancel)
        ok_btn.bind(on_press=on_ok)
        
        reset_popup.open()

    def show_setting_panel(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(
            text='家长设置',
            font_size=28,
            font_name='MicrosoftYaHei',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=0.1
        )
        layout.add_widget(title)
        
        level_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        
        self.level_setting_label = Label(
            text=f'每轮通关关卡数：{int(self.per_round_need_pass)} 关',
            font_size=22,
            font_name='MicrosoftYaHei',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.25
        )
        level_layout.add_widget(self.level_setting_label)
        
        self.temp_setting_value = self.per_round_need_pass
        
        preset_layout = GridLayout(cols=3, size_hint_y=0.35, spacing=5)
        
        for preset in [5, 10, 20]:
            btn = Button(
                text=f'{preset}关',
                font_size=18,
                font_name='MicrosoftYaHei',
                background_color=(0.5, 0.7, 0.9, 1)
            )
            def set_preset(btn_instance, value=preset):
                self.temp_setting_value = value
                self.level_setting_label.text = f'每轮通关关卡数：{value} 关'
            btn.bind(on_press=set_preset)
            preset_layout.add_widget(btn)
        
        level_layout.add_widget(preset_layout)
        
        manual_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
        
        manual_label = Label(
            text='自定义：',
            font_size=20,
            font_name='MicrosoftYaHei',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=0.3
        )
        manual_layout.add_widget(manual_label)
        
        manual_input = TextInput(
            multiline=False,
            font_size=22,
            font_name='MicrosoftYaHei',
            halign='center',
            size_hint_x=0.4
        )
        manual_layout.add_widget(manual_input)
        
        confirm_btn = Button(
            text='确定',
            font_size=18,
            font_name='MicrosoftYaHei',
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_x=0.3
        )
        
        def on_manual_confirm(instance):
            try:
                value = int(manual_input.text.strip())
                if 1 <= value <= 60:
                    self.temp_setting_value = value
                    self.level_setting_label.text = f'每轮通关关卡数：{value} 关'
                    manual_input.text = ''
                else:
                    self.tip_label.text = "请输入1-60之间的数字！"
                    manual_input.text = ''
            except:
                self.tip_label.text = "请输入有效的数字！"
                manual_input.text = ''
        
        confirm_btn.bind(on_press=on_manual_confirm)
        manual_layout.add_widget(confirm_btn)
        
        level_layout.add_widget(manual_layout)
        
        range_label = Label(
            text='(范围：1-60关)',
            font_size=16,
            font_name='MicrosoftYaHei',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.15
        )
        level_layout.add_widget(range_label)
        
        layout.add_widget(level_layout)
        
        change_pwd_btn = Button(
            text='修改密码',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.9, 0.7, 0.5, 1),
            size_hint_y=0.15
        )
        change_pwd_btn.bind(on_press=self.show_change_pwd)
        layout.add_widget(change_pwd_btn)
        
        reset_round_btn = Button(
            text='重置轮次',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.9, 0.5, 0.5, 1),
            size_hint_y=0.15
        )
        reset_round_btn.bind(on_press=self.show_reset_round_dialog)
        layout.add_widget(reset_round_btn)
        
        close_btn = Button(
            text='关闭并保存',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.15
        )
        close_btn.bind(on_press=self.on_setting_close)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        btn_layout.add_widget(close_btn)
        layout.add_widget(btn_layout)
        
        if self.setting_popup:
            self.setting_popup.dismiss()
        
        self.setting_popup = Popup(
            title='',
            content=layout,
            size_hint=(0.9, 0.7),
            background_color=(1, 1, 0.95, 1),
            auto_dismiss=False
        )
        
        self.setting_popup.open()

    def show_reset_round_dialog(self, instance):
        """显示重置轮次确认对话框"""
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        title = Label(
            text='确认重置轮次？',
            font_size=24,
            font_name='MicrosoftYaHei',
            bold=True,
            color=(0.9, 0.3, 0.3, 1),
            size_hint_y=0.3
        )
        layout.add_widget(title)
        
        confirm_label = Label(
            text=f'当前轮次：第 {self.game_state.daily_round + 1} 轮\n重置后将从第1轮开始',
            font_size=20,
            font_name='MicrosoftYaHei',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=0.3
        )
        layout.add_widget(confirm_label)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=15)
        
        cancel_btn = Button(
            text='取消',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.5
        )
        confirm_btn = Button(
            text='确认重置',
            font_size=20,
            font_name='MicrosoftYaHei',
            background_color=(0.9, 0.5, 0.5, 1),
            size_hint_x=0.5
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        layout.add_widget(btn_layout)
        
        reset_popup = Popup(
            title='',
            content=layout,
            size_hint=(0.85, 0.45),
            background_color=(1, 1, 0.95, 1),
            auto_dismiss=False
        )
        
        def on_cancel(instance):
            reset_popup.dismiss()
        
        def on_confirm(instance):
            self.game_state.daily_round = 0
            self.game_state.total_pass_today = 0
            self.game_state.last_stop_level = 1
            self.game_state.save_save_data()
            self.tip_label.text = "轮次已重置！"
            self.speak("轮次已重置")
            reset_popup.dismiss()
            if self.setting_popup:
                self.setting_popup.dismiss()
                self.setting_popup = None
            self.show_start_screen()
        
        cancel_btn.bind(on_press=on_cancel)
        confirm_btn.bind(on_press=on_confirm)
        
        reset_popup.open()

    def show_change_pwd(self, instance):
        if self.setting_popup:
            self.setting_popup.dismiss()
        self.show_pwd_reset()

    def on_setting_close(self, instance):
        self.per_round_need_pass = self.temp_setting_value
        self.game_state.per_round_need_pass = self.per_round_need_pass
        
        config["per_round_need_pass"] = self.per_round_need_pass
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
        
        self.game_state.save_save_data()
        self.tip_label.text = f'设置已保存：每轮 {int(self.per_round_need_pass)} 关'
        self.speak(f'设置已保存，每轮需要通过{int(self.per_round_need_pass)}关')
        
        if self.setting_popup:
            self.setting_popup.dismiss()
            self.setting_popup = None

    def auto_daily_reset(self, dt):
        now = datetime.now().strftime("%Y-%m-%d")
        if now != self.game_state.today_str:
            self.game_state.today_str = now
            self.game_state.daily_round = 0
            self.game_state.total_pass_today = 0
            self.game_state.is_locked_today = False

class MathMainApp(App):
    def build(self):
        return MathLockApp()

if __name__ == '__main__':
    MathMainApp().run()