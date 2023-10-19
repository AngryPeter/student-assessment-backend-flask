import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Counters, Users, Experiment 

# 初始化日志
logger = logging.getLogger('log')


def query_counterbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        return Counters.query.filter(Counters.id == id).first()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def delete_counterbyid(id):
    """
    根据ID删除Counter实体
    :param id: Counter的ID
    """
    try:
        counter = Counters.query.get(id)
        if counter is None:
            return
        db.session.delete(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_counterbyid errorMsg= {} ".format(e))


def insert_counter(counter):
    """
    插入一个Counter实体
    :param counter: Counters实体
    """
    try:
        db.session.add(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def update_counterbyid(counter):
    """
    根据ID更新counter的值
    :param counter实体
    """
    try:
        counter = query_counterbyid(counter.id)
        if counter is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("update_counterbyid errorMsg= {} ".format(e))

def query_user_byphone(phone):
    """
    根据ID查询 User 实体
    :param id: User 时间段
    :return: User 实体
    """
    try:
        return Users.query.filter(Users.phone == phone).first()
    except OperationalError as e:
        logger.info("query_user_byphone errorMsg= {} ".format(e))
        return None
    

def insert_user(user):
    """
    插入一个User实体, 同时更新相关Experiment的时段信息
    :param counter: Counters实体
    """
    try:
        db.session.add(user)
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_user errorMsg= {} ".format(e))


def query_experiment():
    """
    查询全部 Experiment 配置信息
    """
    try:
        return db.session.query(Experiment).all()
    except OperationalError as e:
        logger.info("query_experiment errorMsg= {} ".format(e))
        return None
    

def update_user(user):
    """
    根据 phone 更新 user 时间的值
    :param user 实体
    """
    try:
        have_user = query_user_byphone(user.phone)
        if have_user is None:
            return
        else:
            Users.query.filter(Users.phone == user.phone).update({'time': user.time, 'date': user.date})
            db.session.flush()
            db.session.commit()
    except OperationalError as e:
        logger.info("update_user errorMsg= {} ".format(e))


def delete_user(user):
    """
    根据 phone 删除 User 实体
    :param id: phone
    """
    try:
        have_user = query_user_byphone(user.phone)
        if have_user is None:
            return
        else:
            db.session.query(Users).filter(Users.phone == user.phone, Users.username == user.username).delete()
            db.session.flush()
            db.session.commit()
    except OperationalError as e:
        logger.info("delete_user errorMsg= {} ".format(e))