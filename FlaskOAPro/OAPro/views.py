import os
import hashlib
import datetime
from functools import wraps
from flask import jsonify, flash, url_for, session

from flask import request
from flask import render_template
from flask import redirect

from FlaskOAPro.OAPro import OAPrint
from FlaskOAPro.OAPro.models import *


# # 在整个网站设置变量 name: user.nick_name
# # ("page_process")
# @OAPrint.add_app_template_global
# def page_process():
#     userid = request.cookies.get("userid")
#     user = Person.query.get(int(userid))
#     result = {"name": user.nick_name,
#               "other_attendance": "",
#               "news": "",
#               "person": "",
#               "department": "",
#               "permission": "",
#               }
#     position = user.p_position #用户职位
#     level = position.p_level #用户的职级
#     #判断是否有下属
#     if level > 1:
#         result["other_attendance"] = True
#     else:
#         result["other_attendance"] = False
#
#     #判断是否有新闻权限
#     #获取拥有新闻权限
#     permission = Permission.query.get(1)
#     #查询有该权限的职位
#     news_position_list = permission.p_position
#     #判断当前用户的职位是否在权限范围，如果在，就可以。
#     if position in news_position_list:
#         result["news"] = True
#     else:
#         result["news"] = False
#
#     #判断是否有人事管理权限
#     #查看人事管理权限对应职位
#     person_permission = Permission.query.get(2)
#     person_position = person_permission.p_position
#     if position in person_position:
#         result["person"] = True
#     else:
#         result["person"] = False
#     #判断是否有部门管理权限
#     #董事长有权限管理部门
#     person_permission = Permission.query.get(4)
#     person_position = person_permission.p_position
#     if position in person_position:
#         result["department"] = True
#     else:
#         result["department"] = False
#     # 判断是否有权限管理权限
#     # 董事长有权限管理权限
#     person_permission = Permission.query.get(5)
#     person_position = person_permission.p_position
#     if position in person_position:
#         result["permission"] = True
#     else:
#         result["permission"] = False
#     return result


# 在整个网站设置变量 name: user.nick_name
# ("page_process")
@OAPrint.add_app_template_global
def page_process():
    userid = request.cookies.get("userid")
    user = Person.query.get(int(userid))
    result = {"name": user.nick_name,
              "other_attendance": "",
              "news": "",
              "person": "",
              "department": "",
              "permission": "",
              "records": ""
              }
    # 用户职位
    position = user.p_position
    # 用户的职级
    level = position.p_level
    # 判断是否是董事长
    if level == 5:
        result["other_attendance"] = True
    else:
        result["other_attendance"] = False

    # 判断是否有新闻权限
    # 获取拥有新闻权限
    permission = Permission.query.get(1)
    # 查询有该权限的职位
    news_position_list = permission.p_position
    # 判断当前用户的职位是否在权限范围，如果在，就可以。
    if position in news_position_list:
        result["news"] = True
    else:
        result["news"] = False

    # 判断是否有人事管理权限
    # 查看人事管理权限对应职位
    person_permission = Permission.query.get(2)
    person_position = person_permission.p_position
    if position in person_position:
        result["person"] = True
    else:
        result["person"] = False
    # 判断是否有部门管理权限
    # 董事长有权限管理部门
    person_permission = Permission.query.get(4)
    person_position = person_permission.p_position
    if position in person_position:
        result["department"] = True
    else:
        result["department"] = False
    # 判断是否有权限管理权限
    # 董事长有权限管理权限
    person_permission = Permission.query.get(5)
    person_position = person_permission.p_position
    if position in person_position:
        result["permission"] = True
    else:
        result["permission"] = False

    # 判断是否有查看请假记录权限
    if userid in ['1', '2', '4', '5']:
        result["records"] = True
    else:
        result["records"] = False
    return result


def loginValid(fun):
    @wraps(fun)
    def inner(*args,**kwargs):
        # 获取cookie当中的内容
        username = request.cookies.get("username")
        user_id = request.cookies.get("userid")
        if username and user_id: # 校验cookie有值
            user = Person.query.get(int(user_id))
            if user:
                if user.username == username: # 校验cookie的用户名和数据库当时在的用户名是对应的
                    return fun(*args, **kwargs) # 返回函数
        return redirect("/login/")
    return inner


def hash_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


@OAPrint.route("/")
@loginValid
def index():
    # 查询最新的10条新闻
    big_news = News.query.order_by(News.id.desc()).limit(10)
    # 查询请假审批
    work_table = Attendance.query.filter(Attendance.a_status == '申请中')\
        .order_by(Attendance.apply_time)
    # 查询报销
    exp_table = Expense.query.filter(Expense.a_status == '申请中') \
        .order_by(Expense.apply_time)
    # 查询公章
    seal_table = Seal.query.filter(Seal.a_status == '申请中') \
        .order_by(Seal.apply_time)
    return render_template("index.html", news=big_news, work_tables=work_table,
                           exp_tables=exp_table, seal_tables=seal_table)


# 考勤
@OAPrint.route("/attendance/", methods=["GET", "POST"])
@loginValid
def attendance():
    """
    申请中  1
    审核通过  2
    审核驳回  3
    销假 4
    """
    person_id = request.cookies.get("userid")  # 请假人时当前登陆的用户
    if request.method == "POST":
        reason = request.form.get("reason")
        a_type = request.form.get("a_type")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        # 默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        examine = ""
        # 默认假条状态都是申请中
        a_status = "申请中"

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("attendance.html")

        # 保存假条
        attendance = Attendance()
        attendance.reason = reason
        attendance.a_type = a_type
        attendance.a_date = date
        attendance.start_time = start_time
        attendance.end_time = end_time
        attendance.examine = examine
        attendance.a_status = a_status
        attendance.person_id = person_id
        attendance.apply_time = datetime.datetime.now()
        attendance.save()
        if attendance:
            flash('申请成功')
            return redirect(url_for('OAPrint.attendance'))
    # 考勤展示当前用户的所有假条
    # attendance_list = Person.query.get(int(person_id)).p_attendance
    # 灵活查法
    attendance_list = Attendance.query.filter(
        Attendance.person_id == int(person_id)
    ).order_by(Attendance.start_time)

    return render_template("attendance.html", attendance_list=attendance_list)


# 打卡记录
@OAPrint.route("/record/", methods=["GET", "POST"])
@loginValid
def record():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    # 当前用户的所有会议
    # 灵活查法
    # meet_list = Meet.query.filter(
    #     Meet.person_id == int(person_id)
    # ).order_by(Meet.start_time)

    return render_template("record.html")


# 请假记录
@OAPrint.route("/records/", methods=["GET", "POST"])
@loginValid
def records():
    # 灵活查法
    attendance_list = Attendance.query.filter().order_by(Attendance.apply_time)

    return render_template("records.html", attendance_list=attendance_list)


# 报销
@OAPrint.route("/expense/", methods=["GET", "POST"])
@loginValid
def expense():
    # 申请中  1 申请通过  2 申请驳回  3
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    if request.method == "POST":
        title = request.form.get("title")
        reason = request.form.get("reason")
        amount = request.form.get("amount")
        file = request.files.get("file")
        # 默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        examine = ""
        # 默认状态都是申请中
        a_status = "申请中"
        # 保存报销
        expense = Expense()
        expense.reason = reason
        expense.examine = examine
        expense.a_status = a_status
        expense.person_id = person_id
        time_info = datetime.datetime.now()
        expense.apply_time = time_info
        expense.title = title
        expense.amount = amount
        if file:
            # 图片的名称
            filename = file.filename
            static_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                ), "static"
            )  # 静态路径
            db_path = "files/" + str(time_info)[:19] + filename  # 数据库当中保存的地址
            save_path = os.path.join(static_path, db_path)  # 保存到服务器的地址
            file.save(save_path)  # 保存到服务器
            expense.file = db_path  # 记录路径到数据库
        expense.save()
        if expense:
            flash('申请成功')
            return redirect(url_for('OAPrint.expense'))
    # 考勤展示当前用户的所有假条
    # attendance_list = Person.query.get(int(person_id)).p_attendance
    # 灵活查法
    expense_list = Expense.query.filter(
        Expense.person_id == int(person_id)
    ).order_by(Expense.apply_time)

    return render_template("expense.html", expense_list=expense_list)


# 公章申请
@OAPrint.route("/seal/", methods=["GET", "POST"])
@loginValid
def seal():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    if request.method == "POST":
        reason = request.form.get("reason")
        a_type = request.form.get("a_type")
        # date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        file = request.files.get("file")
        # 默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        examine = ""
        # 默认公章状态都是申请中
        a_status = "申请中"

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("seal.html")

        # 保存公章
        seal = Seal()
        seal.reason = reason
        seal.a_type = a_type
        # seal.a_date = date
        seal.start_time = start_time
        seal.end_time = end_time
        seal.examine = examine
        seal.a_status = a_status
        seal.person_id = person_id
        time_info = datetime.datetime.now()
        seal.apply_time = time_info
        if file:
            # 图片的名称
            filename =  file.filename
            static_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                ), "static"
            )  # 静态路径
            db_path = "files/" + str(time_info)[:19] + filename  # 数据库当中保存的地址
            save_path = os.path.join(static_path, db_path)  # 保存到服务器的地址
            file.save(save_path)  # 保存到服务器
            seal.file = db_path  # 记录路径到数据库
        seal.save()
        flash('申请成功')
        return redirect(url_for('OAPrint.seal'))
    # 展示当前用户的所有公章申请
    # seal_list = Person.query.get(int(person_id)).p_seal
    # 灵活查法
    seal_list = Seal.query.filter(
        Seal.person_id == int(person_id)
    ).order_by(Seal.start_time)

    return render_template("seal.html", seal_list=seal_list)


# 公章审批
@OAPrint.route("/other_seal/")
def other_seal():
    seal_list = []
    # 查询当前用户
    user_id = request.cookies.get("userid")
    # 用户个人信息
    user = Person.query.get(int(user_id))
    # 查询自己的职位
    positions = user.p_position
    if positions.p_level == 5:
        seal_list = Seal.query.filter_by(a_status='申请中').all()
    return render_template("other_seal.html", seal_list=seal_list)


# 商务立项
@OAPrint.route("/establish/", methods=["GET", "POST"])
@loginValid
def establish():
    person_id = request.cookies.get("userid")  # 请假人时当前登陆的用户
    if request.method == "POST":
        reason = request.form.get("reason")
        a_type = request.form.get("a_type")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        # 默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        examine = ""
        # 默认假条状态都是申请中
        a_status = "申请中"

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("attendance.html")

        # 保存假条
        attendance = Attendance()
        attendance.reason = reason
        attendance.a_type = a_type
        attendance.a_date = date
        attendance.start_time = start_time
        attendance.end_time = end_time
        attendance.examine = examine
        attendance.a_status = a_status
        attendance.person_id = person_id
        attendance.save()
    # 考勤展示当前用户的所有假条
    # attendance_list = Person.query.get(int(person_id)).p_attendance
    # 灵活查法
    attendance_list = Attendance.query.filter(
        Attendance.person_id == int(person_id)
    ).order_by(Attendance.start_time)

    return render_template("establish.html", attendance_list=attendance_list)


# 合同审批
@OAPrint.route("/contract/", methods=["GET", "POST"])
@loginValid
def contract():
    person_id = request.cookies.get("userid")  # 请假人时当前登陆的用户
    if request.method == "POST":
        reason = request.form.get("reason")
        a_type = request.form.get("a_type")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        examine = "" #默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        a_status = "申请中" #默认假条状态都是申请中

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("attendance.html")

        # 保存假条
        attendance = Attendance()
        attendance.reason = reason
        attendance.a_type = a_type
        attendance.a_date = date
        attendance.start_time = start_time
        attendance.end_time = end_time
        attendance.examine = examine
        attendance.a_status = a_status
        attendance.person_id = person_id
        attendance.save()
    # 考勤展示当前用户的所有假条
    # attendance_list = Person.query.get(int(person_id)).p_attendance
    # 灵活查法
    attendance_list = Attendance.query.filter(
        Attendance.person_id == int(person_id)
    ).order_by(Attendance.start_time)

    return render_template("contract.html", attendance_list=attendance_list)


# 技术立项
@OAPrint.route("/affairs/", methods=["GET", "POST"])
@loginValid
def affairs():
    person_id = request.cookies.get("userid")  # 请假人时当前登陆的用户
    if request.method == "POST":
        reason = request.form.get("reason")
        a_type = request.form.get("a_type")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        examine = "" #默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        a_status = "申请中" #默认假条状态都是申请中

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("attendance.html")

        # 保存假条
        attendance = Attendance()
        attendance.reason = reason
        attendance.a_type = a_type
        attendance.a_date = date
        attendance.start_time = start_time
        attendance.end_time = end_time
        attendance.examine = examine
        attendance.a_status = a_status
        attendance.person_id = person_id
        attendance.save()
    # 考勤展示当前用户的所有假条
    # attendance_list = Person.query.get(int(person_id)).p_attendance
    # 灵活查法
    attendance_list = Attendance.query.filter(
        Attendance.person_id == int(person_id)
    ).order_by(Attendance.start_time)

    return render_template("affairs.html", attendance_list=attendance_list)


# @OAPrint.route("/other_attendance/")
# def other_attendance():
#     """
#     假条查询
#     """
#     attendance_list = []
#     #下属 是当前部门职位等级低于自己的人
#     #查询当前用户
#     user_id = request.cookies.get("userid")
#     user = Person.query.get(int(user_id)) #用户个人信息
#     #查询自己的职位
#     position = user.p_position
#     #查出自己的部门
#     department = position.p_department
#     #查出自己部门的职位
#     position_list = department.d_position
#     #查查自己部门职位等级小于自己的人
#     for pos in position_list:
#         if pos.p_level < position.p_level:
#             # 对应职位的人
#             # 查到对应职位的人，可能多人
#             persion = pos.p_person
#             # 查询这些人的假条
#             # 循环出每个人
#             for p in persion:
#                 attendance_list.extend(p.p_attendance)
#     return render_template("other_attendance.html", att_list=attendance_list)


# 请假审批（董事长审批所有人）
@OAPrint.route("/other_attendance/")
def other_attendance():
    """
    假条查询
    """
    attendance_list = []
    # 查询当前用户
    user_id = request.cookies.get("userid")
    # 用户个人信息
    user = Person.query.get(int(user_id))
    # 查询自己的职位
    positions = user.p_position
    if positions.p_level == 5:
        attendance_list = Attendance.query.filter_by(a_status='申请中').all()
    return render_template("other_attendance.html", att_list=attendance_list)


# 报销审批（董事长审批所有人）
@OAPrint.route("/other_expense/")
def other_expense():
    """
    报销查询
    """
    expense_list = []
    # 查询当前用户
    user_id = request.cookies.get("userid")
    # 用户个人信息
    user = Person.query.get(int(user_id))
    # 查询自己的职位
    positions = user.p_position
    if positions.p_level == 5:
        expense_list = Expense.query.filter_by(a_status='申请中').all()
    return render_template("other_expense.html", exp_list=expense_list)


# 会议安排
@OAPrint.route("/meeting/", methods=["GET", "POST"])
@loginValid
def meeting():
    person_id = request.cookies.get("userid")  # 当前登陆的用户
    if request.method == "POST":
        title = request.form.get("title")
        room = request.form.get("room")
        # 默认状态都是申请中
        m_status = ""
        reason = request.form.get("reason")
        persons = request.form.get("persons")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        # 默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        examine = ""

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("meeting.html")

        # 保存会议
        meet = Meet()
        meet.title = title
        meet.room = room
        meet.persons = persons
        meet.m_status = m_status
        meet.reason = reason
        meet.start_time = start_time
        meet.end_time = end_time
        meet.examine = examine
        meet.person_id = person_id
        meet.save()
    # # 当前用户的所有会议
    # # meet_list = Person.query.get(int(person_id)).p_meet
    # 灵活查法
    person_list = Person.query.filter().all()
    return render_template("meeting.html", person_list=person_list)


# 我的会议
@OAPrint.route("/schedule/", methods=["GET", "POST"])
@loginValid
def schedule():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    user = Person.query.filter(Person.id == person_id).first()
    # 当前用户的所有会议
    # 灵活查法
    meet_list = Meet.query.filter(
        Meet.person_id == int(person_id)
    ).order_by(Meet.start_time)

    return render_template("schedule.html", meet_list=meet_list)


# 会议室管理
@OAPrint.route("/mine/", methods=["GET", "POST"])
@loginValid
def mine():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    # 当前用户的所有会议
    # 灵活查法
    meet_list = Meet.query.filter(
        Meet.person_id == int(person_id)
    ).order_by(Meet.start_time)

    return render_template("schedule.html", meet_list=meet_list)


# 假条审核
@OAPrint.route("/accept/<a_type>/<int:a_id>/")
def accept(a_type, a_id):
    user_id = request.cookies.get("userid")
    attend = Attendance.query.get(int(a_id))
    # 代表通过
    if a_type == "t":
        a_status = "审核通过"
    # 代表驳回
    elif a_type == "b":
        a_status = "审核驳回"
    else:
        a_status = "申请中"
    attend.a_status = a_status
    attend.examine = Person.query.get(int(user_id)).nick_name
    attend.examine_time = datetime.datetime.now()
    attend.update()

    return redirect("/other_attendance/")


# 报销审核
@OAPrint.route("/accept_exp/<a_type>/<int:a_id>/")
def accept_exp(a_type, a_id):
    user_id = request.cookies.get("userid")
    exp = Expense.query.get(int(a_id))
    if a_type == "t": #代表通过
        a_status = "审核通过"
    elif a_type == "b":#代表驳回
        a_status = "审核驳回"
    else:
        a_status = "申请中"
    exp.a_status = a_status
    exp.examine = Person.query.get(int(user_id)).nick_name
    exp.examine_time = datetime.datetime.now()
    exp.update()

    return redirect("/other_expense/")


# 公章审核
@OAPrint.route("/accept_seal/<a_type>/<int:a_id>/")
def accept_seal(a_type, a_id):
    user_id = request.cookies.get("userid")
    seals = Seal.query.get(int(a_id))
    # 代表通过
    if a_type == "t":
        a_status = "审核通过"
    # 代表驳回
    elif a_type == "b":
        a_status = "审核驳回"
    else:
        a_status = "申请中"
    seals.a_status = a_status
    seals.examine = Person.query.get(int(user_id)).nick_name
    seals.examine_time = datetime.datetime.now()
    seals.update()

    return redirect("/other_seal/")


@OAPrint.route("/department/", methods=["GET", "POST"])
@loginValid
def department():
    if request.method == "POST":
        d_name = request.form.get("d_name")
        d_description = request.form.get("d_des")
        # 二者有值
        if d_name and d_description:
            depart = Department()
            depart.d_name = d_name
            depart.d_description = d_description
            depart.save()
    depart_list = Department.query.all()
    return render_template("department.html", depart_list=depart_list)


@OAPrint.route("/news/", methods=["POST", "GET"])
@loginValid
def news():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        content = request.form.get("content")
        picture = request.files.get("picture")

        news = News()
        news.title = title
        news.author = author
        news.content = content
        news.public_time = datetime.datetime.now()

        if picture:
            # 图片的名称
            filename = picture.filename
            static_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                ), "static"
            )#静态路径
            db_path = "images/"+filename #数据库当中保存的图片地址
            save_path = os.path.join(static_path,db_path) #保存图片到服务器的地址
            picture.save(save_path) #保存图片到服务器
            news.picture = db_path #记录路径到数据库
        news.save()
    news_list = News.query.order_by(News.id.desc())
    return render_template("news.html", news_list=news_list)


@OAPrint.route("/doc/", methods=["POST", "GET"])
@loginValid
def doc():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        content = request.form.get("content")
        picture = request.files.get("picture")

        docs = Doc()
        docs.title = title
        docs.author = author
        doc.content = content
        docs.public_time = datetime.datetime.now()

        if picture:
            # 图片的名称
            filename = picture.filename
            static_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                ),"static"
            )# 静态路径
            db_path = "images/"+filename # 数据库当中保存的图片地址
            save_path = os.path.join(static_path,db_path) # 保存图片到服务器的地址
            picture.save(save_path) # 保存图片到服务器
            docs.picture = db_path # 记录路径到数据库
        docs.save()
    doc_list = Doc.query.order_by(Doc.id.desc())
    return render_template("doc.html", doc_list=doc_list)


@OAPrint.route("/docs_info/<int:doc_id>/", methods=["POST", "GET"])
@loginValid
def docs_info(doc_id):
    article = Doc.query.get(doc_id)
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        content = request.form.get("content")

        article.title = title
        article.author = author
        article.content = content
        article.update()
    return render_template("doc_info.html", article=article)


@OAPrint.route("/news_info/<int:id>/", methods=["POST", "GET"])
@loginValid
def news_info(id):
    article = News.query.get(id)
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        content = request.form.get("content")

        article.title = title
        article.author = author
        article.content = content
        article.update()
    return render_template("news_info.html", article=article)


@OAPrint.route("/del_news/<int:id>/")
@loginValid
def del_news(id):
    # 获取新闻
    article = News.query.get(id)
    # 删除新闻
    article.delete()
    # 跳转页面
    return redirect("/news/")


@OAPrint.route("/del_doc/<int:id>/")
@loginValid
def del_doc(doc_id):
    # 获取文档
    article = Doc.query.get(doc_id)
    # 删除文档
    article.delete()
    # 跳转页面
    return redirect("/doc/")


# 工作流程
@OAPrint.route("/handle/", methods=["GET", "POST"])
@loginValid
def handle():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    if request.method == "POST":
        title = request.form.get("title")
        reason = request.form.get("reason")
        degree = request.form.get("degree")
        user = request.form.get("person")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        # 默认不设置审核人，当人事部员工登陆系统进行审批，那么审批人就是这个员工
        examine = ""
        # 默认日程状态都是处理中
        a_status = "处理中"

        # flask-sqlalchemy 时间字段接受的数据必须是python的datetime格式，需要使用datetime模块构建
        try:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except:
            return render_template("handle.html")

        # 保存日程
        handler = Handle()
        handler.title = title
        handler.reason = reason
        handler.degree = degree
        handler.person = user
        handler.start_time = start_time
        handler.end_time = end_time
        handler.examine = examine
        handler.a_status = a_status
        handler.person_id = person_id
        handler.apply_time = datetime.datetime.now()
        handler.save()
        if handler:
            flash('发布成功')
            return redirect(url_for('OAPrint.handle'))
    # 展示当前用户的所有日程
    # handler_list = Person.query.get(int(person_id)).p_handle
    # 灵活查法
    handler_list = Handle.query.filter(
        Handle.a_status == '处理中').order_by(Handle.start_time)
    person_list = Person.query.filter().all()
    return render_template("handle.html", handler_list=handler_list, person_list=person_list)


# 工作流程--我的待办
@OAPrint.route("/todo/", methods=["GET", "POST"])
@loginValid
def todo():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    user = Person.query.filter(Person.id == person_id).first()

    # 灵活查法
    handler_list = Handle.query.filter(
        Handle.a_status == '处理中', Handle.person == user.nick_name).order_by(Handle.start_time)
    return render_template("todo.html", handler_list=handler_list)


@OAPrint.route("/update_todo/<int:id>/")
@loginValid
def update_todo(id):
    # 获取流程
    handles = Handle.query.get(id)
    # 更新流程
    handles.a_status = '已完成'
    handles.examine_time = datetime.datetime.now()
    handles.update()
    # 跳转页面
    return redirect("/todo/")


# 工作流程--我的已办
@OAPrint.route("/done/", methods=["GET", "POST"])
@loginValid
def done():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    user = Person.query.filter(Person.id == person_id).first()
    # 灵活查法
    handler_list = Handle.query.filter(
        Handle.a_status == '已完成', Handle.person == user.nick_name).order_by(Handle.start_time)
    return render_template("done.html", handler_list=handler_list)


# 工作流程--我创建的
@OAPrint.route("/setup/", methods=["GET", "POST"])
@loginValid
def setup():
    # 当前登陆的用户
    person_id = request.cookies.get("userid")
    # 灵活查法
    handler_list = Handle.query.filter(
        Handle.person_id == person_id).order_by(Handle.start_time)
    return render_template("setup.html", handler_list=handler_list)


@OAPrint.route("/person/<int:page>/", methods=["POST", "GET"])
@loginValid
def person(page=1):
    positions = Position.query.all()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nickname = request.form.get("nick_name")
        position = request.form.get("position")

        p = Person()
        p.username = username
        p.password = hash_password(password)
        p.nick_name = nickname
        p.position_id = position
        p.save()

    page_size = 10
    persion_list = Person.query.paginate(page, page_size)
    if page < 2:
        start = page
    else:
        start = page - 2
    # 获取所有的页码
    page_range = range(1, persion_list.pages+1)[start:page+3]
    return render_template("person.html", **locals())


@OAPrint.route("/del_department/<int:id>/")
@loginValid
def del_department(id):
    # 删除逻辑
    depart = Department.query.get(id)
    depart.delete()
    # 删除完成返回页面
    return redirect("/department/")


@OAPrint.route("/update_department/<int:depart_id>/", methods=["POST", "GET"])
@loginValid
def update_department(depart_id):
    depart = Department.query.get(depart_id)
    if request.method == "POST":
        d_name = request.form.get("d_name")
        d_description = request.form.get("d_des")
        # 二者有值
        if d_name and d_description:
            depart.d_name = d_name
            depart.d_description = d_description
            depart.update()
            return redirect("/department/")

    return render_template("update_department.html", depart=depart)


@OAPrint.route("/position/<int:pos_id>/", methods=["POST", "GET"])
@loginValid
def position(pos_id):
    """
    :param id: 是部门id 用来查询部门，部门和职位是一对多关系，所以可以通过部门查出所有职位
    """
    depart = Department.query.get(pos_id)
    if request.method == "POST":
        p_name = request.form.get("p_name")
        p_description = request.form.get("p_description")
        p_level = request.form.get("p_level")

        p = Position()
        p.p_name = p_name
        p.p_description = p_description
        p.p_level = p_level
        p.department_id = pos_id
        p.save()
    # position_list = Position.query.all()
    position_list = depart.d_position
    return render_template("position.html", **locals())


@OAPrint.route("/login/", methods=["POST", "GET"])
def login():
    if request.cookies.get('username'):
        return redirect(url_for('OAPrint.index'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # 判断用户名是否存在
        user = Person.query.filter(Person.username == username).first()
        if user:
            # 判断密码是否正确
            if hash_password(password) == user.password:
                response = redirect("/")
                response.set_cookie("username", username)
                # cookie 必须是字符串
                response.set_cookie("userid", str(user.id))
                return response
            flash('无效用户名或密码')
            return redirect(url_for('OAPrint.login'))
        else:
            flash('无效用户名或密码')
            return redirect(url_for('OAPrint.login'))

    return render_template("login.html", **locals())


@OAPrint.route("/logout/")
def logout():
    response = redirect("/login/")
    # 删除cookie
    response.delete_cookie("username")
    response.delete_cookie("userid")
    return response


# 个人中心
@OAPrint.route("/myself/", methods=["POST", "GET"])
@loginValid
def myself():
    if request.method == "POST":
        username = request.cookies.get('username')
        user = Person.query.filter(Person.username == username).first()
        phone = request.form.get("input_phone")
        mail = request.form.get("input_mail")
        skill = request.form.get("input_skill")
        address = request.form.get("input_address")
        if phone:
            user.phone = phone
        if mail:
            user.email = mail
        if skill:
            user.skill = skill
        if address:
            user.address = address
        user.update()
        flash('提交成功')
        return redirect(url_for('OAPrint.myself'))

    return render_template('self.html')


# 密码修改
@OAPrint.route("/setpassword/", methods=["POST", "GET"])
@loginValid
def setpassword():
    if request.method == "POST":
        username = request.cookies.get('username')
        user = Person.query.filter(Person.username == username).first()
        old_pw = request.form.get("input_pwd")
        # 判断密码是否正确
        if hash_password(old_pw) == user.password:
            # 比对新密码是否相同
            new_pw = request.form.get("input_new")
            re_new_pw = request.form.get("re_input_new")
            if new_pw != re_new_pw:
                flash('两次输入的新密码不相同，请重新输入')
                return redirect(url_for('OAPrint.setpassword'))
            else:
                user.password = hash_password(new_pw)
                user.update()
                flash('密码修改成功')
                return redirect(url_for('OAPrint.setpassword'))
        else:
            flash('旧密码错误，请重新输入')
            return redirect(url_for('OAPrint.setpassword'))
    return render_template('setpassword.html')


@OAPrint.route("/kpi/")
def kpi():
    result = {
        "department_list": [

        ]
    }

    department_list = Department.query.all()
    for i in department_list:
        count = 0
        for j in i.d_position:
            count += len(j.p_person)
        result["department_list"].append({"department_name": i.d_name, "count": count})
    # 将字典转换为json格式
    return jsonify(result)


@OAPrint.route("/permission/", methods=["POST", "GET"])
def permission():
    if request.method == "POST":
        p_name = request.form.get("p_name")
        p_description = request.form.get("p_description")

        if p_name and p_description:
            p = Permission()
            p.p_name = p_name
            p.p_description = p_description
            p.save()
    per_list = Permission.query.all()
    return render_template("permission.html",per_list = per_list)


@OAPrint.route("/per_position/<int:per_id>/", methods=["POST", "GET"])
def per_position(per_id):
    per = Permission.query.get(per_id)

    pos_list = Position.query.all()
    if request.method == "POST":
        pos_id_list = request.form.getlist("pos_id")
        # 删除之前的关联
        for i in per.p_position:
            per.p_position.remove(
                i
            )
            # 移除的是中间的关系，不会删除数据
            per.update()
        # 从新添加关联
        for each_pos_id in pos_id_list:#循环得到提交的职位id

            per.p_position.append( #搭建关联
                Position.query.get(int(each_pos_id)) #获取具体的权限
            )
            per.update()

    our_pos_id = [i.id for i in per.p_position] #获取自己所有权限的id

    return render_template("per_position.html", **locals())


from FlaskOAPro import api
from flask_restful import Resource
from flask import make_response


class PersonApi(Resource):
    def set_dict(self,obj,models):
        result = {col.name:getattr(obj,col.name) for col in models.__table__.columns}
        return result

    def get(self):
        person = Person.query.filter()
        result = [self.set_dict(p, Person) for p in person]
        response = make_response(jsonify(result))
        return response


api.add_resource(PersonApi, "/api/person/")


@OAPrint.route("/person_page/")
def person_api():
    return render_template("personApi.html")






# @OAPrint.route("/add_data/")
# def add_data():
#     from FlaskOAPro.OAPro.models import Person
#     from pypinyin import lazy_pinyin
#     import random
#
#     first_name = """敬森·邱晓蕴·邱旭晨·邱梓旋·邱诗芙·邱启儒·邱靖蒙·邱靖鑫·邱浩永·邱麒均·邱允泓·邱鹤元·邱梦韵·邱澍辰·邱恺宇·邱偌惜·邱蔚怡·邱灵辉·邱靓秋·邱灿荣·邱伊玲·邱薇琪·邱鹏祎·邱森宁·邱雅彤·邱宇煦·邱归旷·邱梦焓·邱冰清·邱琬芸·邱秦欧·邱忆博·邱轩晗·邱天筠·邱之阳·邱铭萱·邱小婷·邱淑霏·邱修泽·邱恩翔·邱如祎·邱丁茕·邱锦蓉·邱培乐·邱毅晖·邱代姗·邱绪和·邱元兴·邱奇颖·邱歆巧·邱义桦·邱守仁·邱川凯·邱一州·邱诺鑫·邱江静·邱喻安·邱孟博·邱怡盈·邱焱皓""".split(
#         "·邱")
#     last_name = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨"
#     position_list = list(range(8, 14))
#     position_list.append(3)
#
#     for i in last_name:
#         for j in first_name:
#             name = i + j
#             username = "".join(lazy_pinyin(name))
#             p = Person()
#             p.username = username
#             p.password = "e10adc3949ba59abbe56e057f20f883e"
#             p.nick_name = name
#             p.position_id = random.choice(position_list)
#             p.save()
#     return "保存完成"
