# 题目类型模块 - 模块化题目系统
# 预留扩展接口，方便以后添加更高级的数学题目（如几何、初高中数学等）

from abc import ABC, abstractmethod
import random

class QuestionType(ABC):
    """题目类型抽象基类"""
    
    @abstractmethod
    def generate(self, max_num):
        """
        生成题目
        参数：max_num - 最大数字限制
        返回：(题目文本, 答案)
        """
        pass
    
    @abstractmethod
    def get_name(self):
        """获取题目类型名称"""
        pass
    
    @abstractmethod
    def get_description(self):
        """获取题目类型描述"""
        pass

class AdditionQuestion(QuestionType):
    """加法题目"""
    
    def generate(self, max_num):
        # 确保和不超过max_num
        num1 = random.randint(1, max_num)
        num2 = random.randint(1, max_num - num1)
        answer = num1 + num2
        return f"{num1} + {num2} = ?", answer
    
    def get_name(self):
        return "addition"
    
    def get_description(self):
        return "加法"

class SubtractionQuestion(QuestionType):
    """减法题目"""
    
    def generate(self, max_num):
        num1 = random.randint(1, max_num)
        num2 = random.randint(0, min(num1, max_num))
        answer = num1 - num2
        return f"{num1} - {num2} = ?", answer
    
    def get_name(self):
        return "subtraction"
    
    def get_description(self):
        return "减法"

class MultiplicationQuestion(QuestionType):
    """乘法题目"""
    
    def generate(self, max_num):
        num1 = random.randint(1, min(max_num, 12))
        num2 = random.randint(1, min(max_num, 12))
        answer = num1 * num2
        return f"{num1} × {num2} = ?", answer
    
    def get_name(self):
        return "multiplication"
    
    def get_description(self):
        return "乘法"

class DivisionQuestion(QuestionType):
    """除法题目"""
    
    def generate(self, max_num):
        num2 = random.randint(1, min(max_num, 12))
        answer = random.randint(1, min(max_num, 12))
        num1 = num2 * answer
        return f"{num1} ÷ {num2} = ?", answer
    
    def get_name(self):
        return "division"
    
    def get_description(self):
        return "除法"

# ===========================================
# 扩展接口 - 以后可以添加更多题目类型
# ===========================================
# 
# 示例：几何题目
# class GeometryQuestion(QuestionType):
#     """几何题目"""
#     
#     def generate(self, max_num):
#         # 实现几何题目生成逻辑
#         pass
#     
#     def get_name(self):
#         return "geometry"
#     
#     def get_description(self):
#         return "几何"
#
# 示例：初高中代数题目
# class AlgebraQuestion(QuestionType):
#     """代数题目"""
#     
#     def generate(self, max_num):
#         # 实现代数题目生成逻辑
#         pass
#     
#     def get_name(self):
#         return "algebra"
#     
#     def get_description(self):
#         return "代数"
# ===========================================

class QuestionTypeRegistry:
    """题目类型注册器"""
    
    _question_types = {
        "addition": AdditionQuestion(),
        "subtraction": SubtractionQuestion(),
        "multiplication": MultiplicationQuestion(),
        "division": DivisionQuestion(),
    }
    
    @classmethod
    def register(cls, name, question_type):
        """
        注册新的题目类型
        用法：QuestionTypeRegistry.register("geometry", GeometryQuestion())
        """
        if not isinstance(question_type, QuestionType):
            raise ValueError("question_type must be instance of QuestionType")
        cls._question_types[name] = question_type
    
    @classmethod
    def get(cls, name):
        """获取题目类型"""
        return cls._question_types.get(name)
    
    @classmethod
    def get_all_names(cls):
        """获取所有题目类型名称"""
        return list(cls._question_types.keys())
    
    @classmethod
    def create_question(cls, operation, max_num):
        """
        创建题目
        参数：operation - 运算类型名称, max_num - 最大数字限制
        返回：(题目文本, 答案)
        """
        question_type = cls._question_types.get(operation)
        if question_type is None:
            raise ValueError(f"Unknown operation: {operation}")
        return question_type.generate(max_num)

# 便捷函数
def create_question(operation, max_num):
    """创建题目"""
    return QuestionTypeRegistry.create_question(operation, max_num)

def register_question_type(name, question_type):
    """注册新题目类型"""
    QuestionTypeRegistry.register(name, question_type)