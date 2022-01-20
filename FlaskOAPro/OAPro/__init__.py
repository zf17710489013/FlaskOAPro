from flask import Blueprint

# 创建蓝图
# 第一个参数是蓝图的命名
# 第二个参数是蓝图的导入位置

OAPrint = Blueprint("OAPrint", __name__)

from FlaskOAPro.OAPro.views import *