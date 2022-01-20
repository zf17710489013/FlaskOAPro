from FlaskOAPro import make_app
from flask_script import Command,Manager
from flask_migrate import Migrate,MigrateCommand

from FlaskOAPro.OAPro.models import db


# 得到flask app对象
app = make_app()

# 绑定应用和数据库
migrate = Migrate(app, db)


class SayHello(Command):
    def run(self):
        print("hello world")


class OurRun(Command):
    def run(self):
        # app.wsgi_app = MiddleWare(app.wsgi_app)
        app.run(host="0.0.0.0", port=8181, debug=True, use_reloader=True)


# 命令行绑定应用
manage = Manager(app)
# 安装命令
manage.add_command("say_hello", SayHello)
# 安装命令
manage.add_command("run", OurRun)
# 安装命令
manage.add_command("db", MigrateCommand)


if __name__ == '__main__':
    # 启动命令行
    manage.run()

    