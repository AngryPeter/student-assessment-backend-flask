from datetime import datetime

from wxcloudrun import db


# 计数表
class Counters(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Counters'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())


# 用户信息表
class Users(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Users'

    # 设定结构体对应表格的字段
    username = db.Column(db.Text)
    phone = db.Column(db.String(255), primary_key=True)
    date = db.Column(db.Text)
    time = db.Column(db.Text)


# 试验信息配置表
class Experiment(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Experiment'

    # 设定结构体对应表格的字段
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)
    time = db.Column(db.String(255), primary_key=True)
    number = db.Column(db.Integer)
    left_number = db.Column(db.Integer)