#!/usr/local/bin/python3
from functools import wraps
import json,time,sys
from flask import Flask, request, Response, session, render_template, url_for, redirect, jsonify
# from flask.ext import restful
from flask_restful import reqparse, abort, Api, Resource
from bi_sendcoupon_func import *

app = Flask(__name__)
apiloger = Logger('%s/.logs/icoupon_apiloger' %PRO_PATH).set_format('%(asctime)s(%(created)f)-%(levelname)-8s|%(pathname)s|%(module)s|%(funcName)s|%(message)s').set_date(time_replace(ss="%Y%m%d"))
# flasklogger = Logger('%s/.logs/icoupon_flaskloger' %PRO_PATH).set_format('%(asctime)s(%(created)f)-%(levelname)s|%(filename)s|%(funcName)s|%(lineno)s|%(message)s').set_date(time_replace(ss="%Y%m%d"))
# app.logger.addHandler(flasklogger.file_handler)
# flasklogger.logger = app.logger
# flasklogger.logger.setLevel(0)


def dolog_apidecorator(apif):
    @wraps(apif)  # 这个细节很重要 http://blog.csdn.net/hqzxsc2006/article/details/50337865  从#login_required源码中发现 http://docs.jinkan.org/docs/flask-login/_modules/flask/ext/login.html#fresh_login_required
    def do_log():
        apitimer = Timer_(1)
        try:
            # 这里才是API处理部分
            res = apif()
        except Exception as err:
            res = {'status': -500, 'info': str(err)}
        # res = apif()   # if debug=True use this and recommend up 5 lines ;如果debug=True用此行并注释上面5行
        apitimer.toc()
        message = '|'.join([request.method, request.environ['REMOTE_ADDR'], request.environ['PATH_INFO'],
                            json.dumps(request.re_dict), str(res['status']), str(res['info']), str(apitimer.tictoc[-1])])
        apiloger.set_date(time_replace(ss="%Y%m%d"))
        apiloger.do_info(message)
        # flasklogger.set_date(time_replace(ss="%Y%m%d"))
        # flasklogger.logger.info(message)
        # print(Response, vars(Response), Response.status_code, str(Response.status_code) )
        return jsonify(res)
    return do_log


def doverify_api(apif):
    @wraps(apif)
    def doverify():
        request.re_dict = request.values.to_dict()
        # if 'appid' not in request.re_dict or 'token' not in request.re_dict:
        #     return {'status': -600, 'info': 'appid or token missed'}
        # appid = request.re_dict.pop('appid')
        # token = request.re_dict.pop('token')
        # if appid == '10162' and token == 'ABSKGU29U5.HDJ2OI6T90UDS2UGCBJDH498FJPA[=':
        #     res = apif()
        # else:
        #     res = {'status': -550, 'info': 'appid or token problem'}
        res = apif()
        return res
    return doverify


@app.route('/ReadMe', methods=['GET', 'POST'])
def readme():
    return 'hello BIModel-api . it was enchanted to meet you 。.。'


@app.route('/NoopsycheMarketing/geti_merchant_coupon', methods=['POST'])
@dolog_apidecorator
@doverify_api
def coupon_():
    args = {'deve_mode': '0'}
    args.update(request.re_dict)
    if 'merchant_id' not in args or 'merchant_type' not in args or 'prefer_gcode' not in args:
        return_dict = {'status': -400, 'info': 'POST data missed'}
    else:
        return_dict = geti_merchant_coupon(**args)
    return return_dict


@app.route('/NoopsycheMarketing/geti_merchant_coupon_birth', methods=['POST'])
@dolog_apidecorator
@doverify_api
def coupon_birth_():
    args = {'deve_mode': '0'}
    args.update(request.re_dict)

    if 'merchant_id' not in args or 'merchant_type' not in args:
        return_dict = {'status': -400, 'info': 'POST data missed'}
    else:
        return_dict = geti_merchant_coupon_birth(**args)
    return return_dict


@app.route('/NoopsycheMarketing/geti_merchant_budget', methods=['POST'])
@dolog_apidecorator
@doverify_api
def budget_():
    args = {}
    args.update(request.re_dict)
    if 'merchant_id' not in args or 'merchant_type' not in args or 'prefer_gcode' not in args:
        return_dict = {'status': -400, 'info': 'POST data missed'}
    else:
        return_dict = geti_merchant_budget(**args)
    return return_dict


@app.route('/NoopsycheMarketing/geti_merchant_recommende', methods=['POST'])
@dolog_apidecorator
@doverify_api
def recommende():
    args = {}
    args.update(request.re_dict)
    if 'merchant_id' not in args or 'merchant_type' not in args or 'prefer_gcode' not in args:
        return_dict = {'status': -400, 'info': 'POST data missed'}
    else:
        return_dict = geti_merchant_recommende(**args)
    return return_dict


@app.route('/NoopsycheMarketing/show_sredis_status', methods=['POST'])
@doverify_api
def showstatus():
    if 'show_num' not in request.re_dict:
        return_dict = {'status': -400, 'info': 'POST data missed'}
    else:
        return_dict = show_sredis_status(**request.re_dict)
    return jsonify(return_dict)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'LAN':
            app.run(port=config.MODELAPI_PORT_ENV, host=config.WBASE['LOCAL_AREA_IP'], debug=False, threaded=True)
        if sys.argv[1] == 'debug':
            app.run(port=config.MODELAPI_PORT_ENV, host='0.0.0.0', debug=True, threaded=True)
    else:
        app.run(port=config.MODELAPI_PORT_ENV, host='0.0.0.0', debug=False, threaded=True)

