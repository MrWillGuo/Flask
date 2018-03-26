# -*- coding:utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
import hashlib
import xmltodict
import time
from flask import Flask, request

app = Flask(__name__)

'''
/wechat8015?
signature=4cd377eace7abf5fd12857ae1128a83f86595171
&echostr=15923785858641821689
&timestamp=1522029553
&nonce=1680641336
'''

'''

1. 微信服务器将发送GET请求到填写的服务器地址URL上，GET请求携带参数如下表所示：
    signature、timestamp、nonce、echostr

2. 自己后台程序校验
    1）将token、timestamp、nonce三个参数进行字典序排序
    2）将三个参数字符串拼接成一个字符串进行sha1加密
    3）开发者获得加密后的字符串可与signature对比，标识该请求来源于微信

3. 如果对比成功， 返回echostr字符串即可表示和微信连通
'''


@app.route('/wechat8024', methods=['GET', 'POST'])
def wechat8024():
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')
    signature = request.args.get('signature')
    token = 'ITCAST'

    # 1）将token、timestamp、nonce三个参数进行字典序排序
    list = [token, timestamp, nonce]
    list.sort()

    # 2）将三个参数字符串拼接成一个字符串进行sha1加密
    str = ''.join(list)
    sign = hashlib.sha1(str).hexdigest()

    # 3）开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
    if signature == sign:

        # 如果对比成功， 返回echostr字符串即可表示和微信连通. 说明是微信发来的数据
        # 这里利用了Token来做加密, 只有Token一致才说明是微信发的

        if request.method == 'GET':
            return echostr

        # 下面是POST请求
        '''
        1. 发送文本消息, 服务器回复同样的消息: 说什么回什么

        # {'xml':{'name':'value', 'age':'value'}}
        # {'name': 'value', 'age': 'value'}
        #
        # xmltodict['name']
        # xmltodict['age']
        '''

        print request.data

        # 接收xml数据, 并转为字典
        xml_dict = xmltodict.parse(request.data).get('xml')
        # 获取消息类型
        msg_type = xml_dict['MsgType']

        if 'text' == msg_type:
            print '接收到了文本消息'

            # 拼接xml的内容节点
            resp = {
                'ToUserName': xml_dict['FromUserName'],
                'FromUserName': xml_dict['ToUserName'],
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': xml_dict['Content'],
            }
            print xml_dict['Content']

        elif 'voice' == msg_type:
            print '接收到了语音消息'

            # 拼接xml的内容节点
            resp = {
                'ToUserName': xml_dict['FromUserName'],
                'FromUserName': xml_dict['ToUserName'],
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': xml_dict['Recognition'],
            }
            print xml_dict['Recognition']

        elif 'event' == msg_type:
            print '接收到了关注/取关消息'
            event = xml_dict['Event']

            if 'subscribe' == event:

                # 拼接xml的内容节点
                resp = {
                    'ToUserName': xml_dict['FromUserName'],
                    'FromUserName': xml_dict['ToUserName'],
                    'CreateTime': time.time(),
                    'MsgType': 'text',
                    'Content': '你好, 感谢你的关注',
                }
                print '你好, 感谢你的关注'

                if xml_dict['EventKey']:
                    # 如果有EventKey的值, 说明是二维码扫描关注了公众号
                    resp["Content"] = "被别人关注了;场景值是：%s" % xml_dict.get("EventKey")
                    print '感谢你的关注, 二维码扫描'

            elif 'unsubscribe' == event:
                print '被别人取消了关注'
                resp = None

            else:
                resp = None

        else:
            # 拼接xml的内容节点
            resp = {
                'ToUserName': xml_dict['FromUserName'],
                'FromUserName': xml_dict['ToUserName'],
                'CreateTime': time.time(),
                'MsgType': 'text',
                'Content': '不认识的类型',
            }
            print '不认识的类型'

        if resp:
            # 拼接xml根节点
            resp = {'xml': resp}
            # 将字典转换成xml返回
            return xmltodict.unparse(resp)
        else:
            return ''

    return ''


if __name__ == '__main__':
    app.run(debug=True, port=8024)
