#安装wtf插件安装的模块
import wtforms #表单字段
from flask_wtf import FlaskForm #表单结构
from wtforms import validators,ValidationError


class OurValid:
    def __init__(self, message):
        self.message = message

    def __call__(self,  form, field):
        data = field.data
        pull = ["admin", "他的爸爸", "NB", "sb"]
        if data in pull:
            raise ValidationError(self.message)


class OurForm(FlaskForm):
    """
    定义自己的表单
    """
    # 定义表单字段和类型
    username = wtforms.StringField(label="用户名:",validators = [
        validators.Length(min = 2,max = 12,message="字段的长度必须是6-12之间"), #设定当前表单的字符长度最少6个长度，最多12个长度
        OurValid(message="用户名不可以是敏感词")
    ]) #定义字符串类型的表单
    password = wtforms.PasswordField(label="密码:") #定义密码类型的表单
    position = wtforms.IntegerField(label="职业:") #定义整形表单