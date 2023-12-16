from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.dao import query_experiment, insert_user, update_user, query_user_byphone, delete_user, search_user
from wxcloudrun.model import Counters, Users
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response, make_nouser_response
import requests
import json
from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
# https://juejin.cn/post/7033614049862483975

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('manage.html', have_user=False)


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
    all_exper_list = []
    for exp in info:
        if exp.name not in all_exper_list:
            all_exper_list.append(exp.name)
        if exp.left_number > 0:
            final_info.append([str(exp.date), exp.time, exp.name])
    return make_succ_response([final_info, all_exper_list])

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
        code = update_user(user)
        if code == -1:
            return make_err_response(user.exper_name)
        return make_succ_empty_response()
    elif params['type'] == 'select':
        quser = Users()
        quser.username = params['name']
        quser.phone = params['phone']
        user_list = query_user_byphone(quser)
        if user_list is None:
            return make_nouser_response()
        else:
            info = []
            for user in user_list:
                info.append([user.username, user.phone, str(user.date), user.time, user.exper_name])
            return make_succ_response(info)
    elif params['type'] == 'delete':
        user = Users()
        user.username = params['name']
        user.phone = params['phone']
        user.exper_name = params['exper_name']
        code = delete_user(user)
        if code == -1:
            return make_err_response('未查到报名信息')
        return make_succ_empty_response()
    else:
        return make_err_response('type参数错误')
    

# 手机号获取路由
@app.route('/phone', methods=['POST'])
def get_phone_number():
    params = request.get_json()
    # response = requests.get("http://api.weixin.qq.com/wxa/getwxadevinfo")
    # 拼接 Header 中的 x-wx-openid 到接口中
    api = f"http://api.weixin.qq.com/wxa/getopendata?openid={request.headers['x-wx-openid']}"
    response = requests.post(api, json={
        "cloudid_list": [params['cloudid']] # 传入需要换取的 CloudID
    }, headers={
        'Content-Type': 'application/json'
    })
    # data = response.json()['data_list'][0]
    try:
        data = response.json()['data_list'][0] # 从回包中获取手机号信息
        phone = json.loads(data['json'])['data']['phoneNumber']
        # 将手机号发送回客户端，此处仅供示例
        # 实际场景中应对手机号进行打码处理，或仅在后端保存使用
        return make_succ_response(phone)
    except Exception as e:
        return make_err_response("fail")
    

@app.route('/search', methods=['POST'])
def get_exper_info():
    """
    :return: 实验名字
    """
    form = request.form
    users = search_user(form["name"], form["date"], form["time"])
    appid = "1400876767"  # 自己应用ID
    appkey = "32a0a7549fbf3db5ad50dfaaa9ba2ca3"  # 自己应用Key
    sms_sign = "未来科技与组织行为公众号" # 自己腾讯云创建签名时填写的签名内容（使用公众号的话这个值一般是公众号全称或简称）
    # sender = SmsSingleSender(appid, appkey)
    template_id = "2021233"
    sender = SmsSingleSender(appid, appkey)
    usernames = []
    for user in users:
        # {1}同学您好！您已成功报名我们的实验：{2}，请在 {3} 来 {4} 参加实验。感谢您的参与，祝好！
        usernames.append(user.username)
        param_list = [user.username, user.exper_name, user.date + " " + user.time, "北京市海淀区世纪科贸大厦C座16楼1604（近清华大学东南门）"]
        try:
            response = sender.send_with_param(86, user.phone, template_id, param_list, sign=sms_sign)
        except HTTPError as e:
            response = {'result': 1000, 'errmsg': "网络异常发送失败"}
            return make_err_response("网络异常发送失败")
    return make_succ_response(usernames)
    # expers = query_experiment()
    # nameList = []
    # for exper in expers:
    #     if exper.name not in nameList:
    #         nameList.append(exper.name)
    # return make_succ_response(nameList)