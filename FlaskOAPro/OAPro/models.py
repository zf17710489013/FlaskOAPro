from FlaskOAPro import db
from werkzeug.security import generate_password_hash, check_password_hash


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Person(Base):
    """
    用户表，记录所有职员的个人信息
    """
    username = db.Column(db.String(32), unique=True)  # 登陆名 必填 不可以重复
    password = db.Column(db.String(32))  # 密码 必填

    nick_name = db.Column(db.String(32)) # 姓名 必填
    age = db.Column(db.Integer,nullable=True) # 年龄 注册后完善 可以为null
    gender = db.Column(db.String(16),nullable = True) # 性别 注册后完善 可以为null
    skill = db.Column(db.String(128),nullable = True) #擅长  注册后完善 可以为null
    phone = db.Column(db.String(16),nullable = True) # 电话 注册后完善 可以为null
    email = db.Column(db.String(32),nullable = True) # 邮箱 注册后完善 可以为null
    address = db.Column(db.Text,nullable = True) # 用户地址 注册后完善 可以为null
    score = db.Column(db.Float,default=1) #绩效 默认为1

    position_id = db.Column(db.Integer,db.ForeignKey("position.id")) #Position 职位表外键

    p_attendance = db.relationship(
        "Attendance",
        backref = "a_person"
    ) # 反向映射 假条表

    p_expense = db.relationship(
        "Expense",
        backref="e_person"
    )  # 反向映射 报销表

    p_seal = db.relationship(
        "Seal",
        backref="s_person"
    )  # 反向映射 公章表

    p_handle = db.relationship(
        "Handle",
        backref="h_person"
    )  # 反向映射 流程表


pos_per = db.Table(
    "pos_per",
    db.Column("pos_id",db.Integer,db.ForeignKey("position.id")), #职位的外键
    db.Column("per_id", db.Integer, db.ForeignKey("permission.id")),  # 权限的外键
) # 职位和权限的多对多中间表


class Position(Base):
    """
    职位表
    """
    p_name = db.Column(db.String(32)) #名称
    p_description = db.Column(db.Text) #描述
    p_level = db.Column(db.Integer) #职级

    p_person = db.relationship(
        "Person",
        backref="p_position"
    ) #反向映射向 员工

    department_id = db.Column(db.Integer, db.ForeignKey("department.id")) #外键指向部门表

    p_permission = db.relationship(
        "Permission",
        secondary="pos_per",
        backref="p_position"
    ) #反向映射权限表，中间表是pos_per


class Permission(Base):
    """
    权限表
    """
    p_name = db.Column(db.String(32)) #名称
    p_description = db.Column(db.Text) #描述


class Department(Base):
    """
    部门表
    """
    d_name = db.Column(db.String(32)) #名称
    d_description = db.Column(db.Text) #描述

    d_position = db.relationship(
        "Position",
        backref="p_department"
    ) #反向映射职位


class Attendance(Base):
    """
    假条（考勤）表
    """
    reason = db.Column(db.Text) # 请假原因 自己定义
    a_type = db.Column(db.String(32)) # 假期类型 事假 婚嫁 产假 病假 年假 调休
    a_date = db.Column(db.Float) # 假期时长 支持（0.5）天
    start_time = db.Column(db.DateTime) # 开始时间
    end_time = db.Column(db.DateTime) # 结束时间
    examine = db.Column(db.String(32)) # 审批人 指定人  用户id
    a_status = db.Column(db.String(32)) # 假条状态 申请中 审核通过 审核驳回 销假

    # 申请时间
    apply_time = db.Column(db.DateTime)
    # 审批时间
    examine_time = db.Column(db.DateTime)

    person_id = db.Column(db.Integer, db.ForeignKey("person.id")) #外键，指向员工表

    #请假人 谁申请，就是谁，id 和person进行关联


class Handle(Base):
    """
    工程流程表
    """
    # 内容
    title = db.Column(db.Text)
    # 备注
    reason = db.Column(db.Text)
    # 重要程度
    degree = db.Column(db.String(32))
    # 处理人
    person = db.Column(db.String(32))
    # 开始时间
    start_time = db.Column(db.DateTime)
    # 结束时间
    end_time = db.Column(db.DateTime)
    # 状态 处理中 已完成
    a_status = db.Column(db.String(32))

    # 发起时间
    apply_time = db.Column(db.DateTime)
    # 完成时间
    examine_time = db.Column(db.DateTime)
    # 外键，指向员工表
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))

    # 创建人 谁创建，就是谁，id 和person进行关联


class Seal(Base):
    """
    公章表
    """
    reason = db.Column(db.Text) # 用章原因 自己定义
    a_type = db.Column(db.String(32)) # 公章类型
    start_time = db.Column(db.DateTime) # 开始时间
    end_time = db.Column(db.DateTime) # 结束时间
    examine = db.Column(db.String(32)) # 审批人 指定人  用户id
    a_status = db.Column(db.String(32)) # 状态 申请中 审核通过 审核驳回

    # 申请时间
    apply_time = db.Column(db.DateTime)
    # 审批时间
    examine_time = db.Column(db.DateTime)

    person_id = db.Column(db.Integer, db.ForeignKey("person.id")) #外键，指向员工表

    # 申请人 谁申请，就是谁，id 和person进行关联
    file = db.Column(db.String(128))  # 文件


class Expense(Base):
    """
    报销表
    """
    title = db.Column(db.String(32))
    reason = db.Column(db.Text) # 报销内容 自己定义
    amount = db.Column(db.String(32))
    examine = db.Column(db.String(32)) # 审批人 指定人  用户id
    a_status = db.Column(db.String(32)) # 状态 申请中 审核通过 审核驳回

    # 申请时间
    apply_time = db.Column(db.DateTime)
    # 审批时间
    examine_time = db.Column(db.DateTime)
    # 外键，指向员工表
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))

    # 申请人 谁申请，就是谁，id 和person进行关联
    file = db.Column(db.String(128))  # 文件


class News(Base):
    """
    新闻表
    """
    # 标题
    title = db.Column(db.String(32))
    # 作者
    author = db.Column(db.String(32))
    # 内容
    content = db.Column(db.Text)
    # 发表日期
    public_time = db.Column(db.Date)
    # 图片  可以为空
    picture = db.Column(db.String(128),nullable = True)


class Doc(Base):
    """
    文档表
    """
    # 标题
    title = db.Column(db.String(32))
    # 作者
    author = db.Column(db.String(32))
    # 内容
    content = db.Column(db.Text)
    # 发布日期
    public_time = db.Column(db.Date)
    # 图片  可以为空
    picture = db.Column(db.String(128),nullable = True)


class Meet(Base):
    """
    会议表
    """
    # 会议主题
    title = db.Column(db.Text)
    # 会议室
    room = db.Column(db.String(32))
    # 参会人员
    persons = db.Column(db.String(32))
    # 开始时间
    start_time = db.Column(db.DateTime)
    # 结束时间
    end_time = db.Column(db.DateTime)
    reason = db.Column(db.String(32))
    # 会议状态  待审批 已审批 已开始 已结束 我参加的
    m_status = db.Column(db.String(32))
    # # 会议类型
    # m_type = db.Column(db.String(32))
    # 外键，指向员工表
    # 谁申请，就是谁，id 和person进行关联
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
