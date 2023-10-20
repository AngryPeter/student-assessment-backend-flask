from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.dao import query_experiment, insert_user, update_user, query_user_byphone, delete_user
from wxcloudrun.model import Counters, Experiment, Users
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response, make_nouser_response


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


# 管理员后端路由
@app.route('/user', methods=['GET'])
def experiment_info_list():
    info = query_experiment()
    final_info = []
    for exp in info:
        if exp.left_number > 0:
            final_info.append([str(exp.date), exp.time, exp.name])
    return make_succ_response(final_info)

# 管理员后端路由
@app.route('/user', methods=['POST'])
def user_action():
    params = request.get_json()
    if params['type'] == 'sign':    # 报名
        user = Users()
        user.username = params['name']
        user.phone = params['phone']
        user.date = datetime.strptime(params['date'], '%Y-%m-%d').date()
        user.time = params['time']
        user.exper_name = params['exper_name']
        code = insert_user(user)
        if code == -1:
            return make_err_response('已报名实验')
        return make_succ_empty_response()
    elif params['type'] == 'modify':    # 修改报名时间
        user = Users()
        user.username = params['name']
        user.phone = params['phone']
        user.date = datetime.strptime(params['date'], '%Y-%m-%d').date()
        user.time = params['time']
        user.exper_name = params['exper_name']
        update_user(user)
        return make_succ_empty_response()
    elif params['type'] == 'select':
        user = query_user_byphone(params['phone'])
        if user is None:
            return make_nouser_response()
        else:
            info = []
            info.append(user.username)
            info.append(user.phone)
            info.append(str(user.date))
            info.append(user.time)
            info.append(user.exper_name)
            return make_succ_response(info)
    elif params['type'] == 'delete':
        user = Users()
        user.username = params['name']
        user.phone = params['phone']
        user.exper_name = params['exper_name']
        delete_user(user)
        return make_succ_empty_response()
    else:
        return make_err_response('type参数错误')