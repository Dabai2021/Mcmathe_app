# UI组件模块

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from config import *

def create_button(text, bg_color, font_size=24, on_press=None):
    btn = Button(
        text=text,
        font_size=font_size,
        font_name='MicrosoftYaHei',
        background_color=bg_color,
        color=BUTTON_TEXT_COLOR
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn

def create_label(text, font_size=24, color=INFO_TEXT_COLOR, bold=False):
    return Label(
        text=text,
        font_size=font_size,
        font_name='MicrosoftYaHei',
        color=color,
        bold=bold
    )

def create_progress_bar():
    return ProgressBar(
        max=100,
        value=0,
        size_hint_y=0.1
    )

def create_question_box():
    box = BoxLayout(orientation='vertical', size_hint_y=0.25)
    with box.canvas.before:
        Color(*QUESTION_BG)
        Rectangle(pos=box.pos, size=box.size)
    box.bind(pos=lambda self, pos: setattr(self, 'canvas.before.children[1].pos', pos))
    box.bind(size=lambda self, size: setattr(self, 'canvas.before.children[1].size', size))
    return box

def create_pwd_popup(on_confirm, on_cancel):
    layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
    
    title = create_label('请输入家长密码', font_size=24, color=(0.2, 0.4, 0.8, 1), bold=True)
    layout.add_widget(title)
    
    pwd_input = TextInput(
        multiline=False,
        password=True,
        font_size=24,
        font_name='MicrosoftYaHei',
        halign='center',
        size_hint_y=0.2
    )
    layout.add_widget(pwd_input)
    
    forgot_label = Label(
        text='忘记密码？',
        font_size=18,
        font_name='MicrosoftYaHei',
        color=(0.2, 0.5, 0.9, 1),
        size_hint_y=0.15
    )
    layout.add_widget(forgot_label)
    
    btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
    
    cancel_btn = create_button('取消', (0.7, 0.7, 0.7, 1))
    confirm_btn = create_button('确认', (0.2, 0.8, 0.2, 1))
    
    btn_layout.add_widget(cancel_btn)
    btn_layout.add_widget(confirm_btn)
    layout.add_widget(btn_layout)
    
    popup = Popup(
        title='',
        content=layout,
        size_hint=(0.85, 0.5),
        background_color=(1, 1, 0.95, 1),
        auto_dismiss=False
    )
    
    def handle_confirm(instance):
        on_confirm(pwd_input.text.strip())
    
    def handle_cancel(instance):
        on_cancel()
        popup.dismiss()
    
    confirm_btn.bind(on_press=handle_confirm)
    cancel_btn.bind(on_press=handle_cancel)
    
    return popup, forgot_label

def create_setting_panel(game):
    layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
    title = create_label('家长设置', font_size=28, color=(0.2, 0.4, 0.8, 1), bold=True)
    title.size_hint_y = 0.1
    layout.add_widget(title)
    
    level_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
    
    level_label = create_label(f'每轮通关关卡数：{int(game.per_round_need_pass)} 关', font_size=22, color=(0.3, 0.3, 0.3, 1))
    level_label.size_hint_y = 0.25
    level_layout.add_widget(level_label)
    
    preset_layout = GridLayout(cols=3, size_hint_y=0.35, spacing=5)
    
    for preset in [5, 10, 20]:
        btn = create_button(f'{preset}关', (0.5, 0.7, 0.9, 1), font_size=18)
        def set_preset(btn_instance, value=preset, label=level_label):
            game.temp_setting_value = value
            label.text = f'每轮通关关卡数：{value} 关'
        btn.bind(on_press=set_preset)
        preset_layout.add_widget(btn)
    
    level_layout.add_widget(preset_layout)
    
    manual_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
    
    manual_label = create_label('自定义：', font_size=20, color=(0.3, 0.3, 0.3, 1))
    manual_label.size_hint_x = 0.3
    manual_layout.add_widget(manual_label)
    
    manual_input = TextInput(
        multiline=False,
        font_size=22,
        font_name='MicrosoftYaHei',
        halign='center',
        size_hint_x=0.4
    )
    manual_layout.add_widget(manual_input)
    
    confirm_btn = create_button('确定', (0.2, 0.8, 0.2, 1), font_size=18)
    confirm_btn.size_hint_x = 0.3
    
    def on_manual_confirm(instance, label=level_label, input_field=manual_input):
        try:
            value = int(input_field.text.strip())
            if 1 <= value <= 60:
                game.temp_setting_value = value
                label.text = f'每轮通关关卡数：{value} 关'
                input_field.text = ''
            else:
                game.tip_label.text = "请输入1-60之间的数字！"
                input_field.text = ''
        except:
            game.tip_label.text = "请输入有效的数字！"
            input_field.text = ''
    
    confirm_btn.bind(on_press=on_manual_confirm)
    manual_layout.add_widget(confirm_btn)
    
    level_layout.add_widget(manual_layout)
    
    range_label = create_label('(范围：1-60关)', font_size=16, color=(0.6, 0.6, 0.6, 1))
    range_label.size_hint_y = 0.15
    level_layout.add_widget(range_label)
    
    layout.add_widget(level_layout)
    
    change_pwd_btn = create_button('修改密码', (0.9, 0.7, 0.5, 1), font_size=20)
    change_pwd_btn.size_hint_y = 0.15
    layout.add_widget(change_pwd_btn)
    
    close_btn = create_button('关闭并保存', (0.2, 0.8, 0.2, 1), font_size=20)
    close_btn.size_hint_y = 0.15
    
    btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
    btn_layout.add_widget(close_btn)
    layout.add_widget(btn_layout)
    
    return layout, level_label, manual_input, close_btn, change_pwd_btn